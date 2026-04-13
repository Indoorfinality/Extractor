import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from ..models.extraction_document import ExtractionDocument
from sqlalchemy.sql import func


# Anchor to this file's location so the path is correct regardless of CWD.
# This file lives at: backend/app/services/document_service.py
# → parents[2] = backend/
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def save_document(file: UploadFile, studio_id: int, db: Session, uploaded_by: int = 1):
    """Save uploaded PDF and store metadata in database"""

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail = "Only PDF files are allowed")
    
    studio_dir = UPLOAD_DIR / str(studio_id)
    studio_dir.mkdir(parents=True, exist_ok=True)

    file_path = studio_dir / file.filename

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    document = db.query(ExtractionDocument).filter(
        ExtractionDocument.studio_id == studio_id,
        ExtractionDocument.filename == file.filename
    ).first()

    if document:
        document.size = os.path.getsize(file_path)
       
        document.uploaded_at = func.now()
    else:
        document = ExtractionDocument(
            filename=file.filename,
            file_path=str(file_path),
            studio_id=studio_id,
            uploaded_by=uploaded_by,
            size=os.path.getsize(file_path)
        )
        db.add(document)
        
    db.commit()
    db.refresh(document)
    return document
