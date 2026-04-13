from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from typing import List
import os

from ..dependencies import get_db
from ..models.extraction_document import ExtractionDocument
from ..schemas.document import DocumentOut
from ..services.document_service import save_document, UPLOAD_DIR

router = APIRouter()

@router.post("/upload", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    studio_id: int = Query(..., description="Studio ID to associate the document with"),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    MAX_FILE_SIZE = 50 * 1024 * 1024
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 50MB limit")
    
    document = save_document(file=file, studio_id=studio_id, db=db,
                             uploaded_by=1)
    return document


@router.get("/file/{doc_id}")
def get_document_file(doc_id: int, db: Session = Depends(get_db)):
    """Serve the stored PDF so the frontend can embed it in an iframe."""
    doc = db.query(ExtractionDocument).filter(ExtractionDocument.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    pdf_path = Path(doc.file_path)
    if not pdf_path.is_absolute():
        repo_root = UPLOAD_DIR.parent
        pdf_path = repo_root / pdf_path

    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        str(pdf_path),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=\"{doc.filename}\""},
    )


@router.get("/{studio_id}", response_model=List[DocumentOut])
def list_documents(
    studio_id: int,
    db: Session = Depends(get_db)
):
    documents = db.query(ExtractionDocument).filter(
        ExtractionDocument.studio_id == studio_id
    ).order_by(ExtractionDocument.uploaded_at.desc()).all()

    unique_documents = []
    seen = set()
    for doc in documents:
        if doc.filename not in seen:
            unique_documents.append(doc)
            seen.add(doc.filename)

    return unique_documents