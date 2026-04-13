from pathlib import Path
from typing import Any, Dict, List, Tuple
import json
import re
import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Header
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..models.extraction_document import ExtractionDocument
from ..models.field_prompt import FieldPrompt
from ..models.prompt_studio import PromptStudio
from ..schemas.extraction import ExtractionRunRequest, ExtractionRunResponse
from ..services.openai_extractor import extract_fields_from_pdf
from ..models.extraction_result import ExtractionResult
from ..models.api_deployment import ApiDeployment

router = APIRouter(tags=["extraction"])


def _outputs_dir() -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "backend" / "outputs"


def _safe_dirname(name: str) -> str:
    """Convert a studio/file name into a safe directory name."""
    return re.sub(r"[^\w\-.]", "_", name).strip("_") or "unnamed"


def _normalize_extracted_fields(value: Any) -> Dict[str, Any]:
    """
    Normalize model output into the dict shape expected by API/schema.
    Accepts:
    - dict (as-is)
    - list with one dict element (unwrap)
    """
    if isinstance(value, dict):
        return value
    if isinstance(value, list) and len(value) == 1 and isinstance(value[0], dict):
        return value[0]
    raise HTTPException(
        status_code=422,
        detail="Extractor returned invalid shape for extracted_fields; expected object.",
    )


#===========result==================
@router.get("/result")
def get_extraction_result(studio_id: int, document_id: int, db: Session = Depends(get_db)):
    """
    Fetch the most-recent persisted extraction result for a given
    (studio_id, document_id) pair.  Returns 404 if none exists yet.
    """
    result = (
        db.query(ExtractionResult)
        .filter(
            ExtractionResult.studio_id == studio_id,
            ExtractionResult.document_id == document_id,
        )
        .order_by(ExtractionResult.id.desc())
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="No extraction result found")

    return {
        "extracted_fields": result.extracted_data,
        "usage": result.usage,
        "raw_output": result.raw_output,
        "created_at": result.created_at.isoformat() if result.created_at else None,
        "updated_at": result.updated_at.isoformat() if result.updated_at else None,
    }

#=========================Run Extraction================================
@router.post("/run", response_model=ExtractionRunResponse)
def run_extraction(payload: ExtractionRunRequest, db: Session = Depends(get_db)):
    studio_id = payload.studio_id
    document_id = payload.document_id

    doc = (
        db.query(ExtractionDocument)
        .filter(
            ExtractionDocument.id == document_id,
            ExtractionDocument.studio_id == studio_id,
        )
        .first()
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    studio = db.query(PromptStudio).filter(PromptStudio.id == studio_id).first()
    studio_name = _safe_dirname(studio.name) if studio else str(studio_id)

    prompts: List[FieldPrompt] = (
        db.query(FieldPrompt)
        .filter(FieldPrompt.studio_id == studio_id)
        .order_by(FieldPrompt.id.asc())
        .all()
    )

    field_prompts: List[Tuple[str, str]] = [
        (p.field_name, p.prompt_text) for p in prompts
    ]

    try:
        pdf_path = Path(doc.file_path)
        if not pdf_path.is_absolute():
            repo_root = Path(__file__).resolve().parents[3]
            pdf_path = repo_root / pdf_path
        extracted_fields, usage, raw_output = extract_fields_from_pdf(
            pdf_path, field_prompts
        )
        extracted_fields = _normalize_extracted_fields(extracted_fields)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Extraction failed: {e}")

    pdf_stem = _safe_dirname(Path(doc.filename).stem)
    out_dir = _outputs_dir() / studio_name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{pdf_stem}.json"

    payload_to_save = {
        "studio_id": studio_id,
        "studio_name": studio.name if studio else str(studio_id),
        "document_id": document_id,
        "source_filename": doc.filename,
        "extracted_fields": extracted_fields,
        "usage": usage,
        "raw_output": raw_output,
    }

    out_path.write_text(
        json.dumps(payload_to_save, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    existing = db.query(ExtractionResult).filter(
        ExtractionResult.document_id == document_id,
        ExtractionResult.studio_id == studio_id,
    ).first()

    if existing:
        existing.extracted_data = extracted_fields
        existing.usage = usage
        existing.raw_output = raw_output
        db.commit()
        db.refresh(existing)
        result_record = existing
    else:
        result_record = ExtractionResult(
            studio_id=studio_id,
            document_id=document_id,
            extracted_data=extracted_fields,
            usage=usage,
            raw_output=raw_output,
        )
        db.add(result_record)
        db.commit()
        db.refresh(result_record)

    return ExtractionRunResponse(
        extracted_fields=extracted_fields,
        output_path=str(out_path),
        usage=usage,
        raw_output=raw_output,
    )


#===========================Public API ENDPOINT============================


@router.post("/extract/{deployment_name}",response_model = ExtractionRunResponse)

async def public_extract(
    deployment_name: str, 
    file: UploadFile = File(...),
    x_api_key: str = Header(None, alias= "X-API-Key"),
    db: Session = Depends(get_db)):
    """
    Public API endpoint for deployed studios.
    Usage:
        POST /api/extract/procurewizard-api
        Header: X-API-Key: sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
        Body: PDF file (multipart/form-data)
    """

    if not x_api_key:
        raise HTTPException(status_code = 401, detail = "Missing X-API-Key header")

    deployment = db.query(ApiDeployment).filter(
        ApiDeployment.name == deployment_name,
        ApiDeployment.api_key == x_api_key,
        ApiDeployment.is_active == True
    ).first()

    if not deployment:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")
    
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code = 400, detail = "Only pdf files are allowed")

    with tempfile.NamedTemporaryFile(delete = False, suffix = '.pdf') as tmp:
        tmp.write(await file.read())
        temp_pdf_path = Path(tmp.name)

    try:

        prompts: List[FieldPrompt]= (
            db.query(FieldPrompt).filter(FieldPrompt.studio_id == deployment.studio_id).order_by(FieldPrompt.id.asc()).all()
        )
    
        if not prompts:
            raise HTTPException(status_code= 400, detail = "No prompts configured in this studio")
        
        field_prompts:List[Tuple[str,str]] = [(p.field_name, p.prompt_text) for p in prompts]

        extracted_fields, usage, raw_output = extract_fields_from_pdf(temp_pdf_path, field_prompts)
        extracted_fields = _normalize_extracted_fields(extracted_fields)
    
        result_record = ExtractionResult(
            studio_id=deployment.studio_id,
            document_id=None,       
            extracted_data=extracted_fields,
            usage=usage,
            raw_output=raw_output,
        )

        db.add(result_record)
        db.commit()
        db.refresh(result_record)

        return ExtractionRunResponse(
            extracted_fields= extracted_fields,
            output_path="",
            usage = usage,
            raw_output=raw_output
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code = 500, detail=f"Extraction failed: {str(e)}")

    finally:
        if temp_pdf_path.exists():
            os.unlink(temp_pdf_path)

    



    






