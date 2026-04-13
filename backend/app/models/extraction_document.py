from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class ExtractionDocument(Base):
    __tablename__ = "extraction_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    studio_id = Column(Integer, ForeignKey("prompt_studios.id", ondelete="CASCADE"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    size = Column(BigInteger)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    studio = relationship("PromptStudio", back_populates="documents")
    extraction_results = relationship("ExtractionResult", back_populates="document", cascade="all, delete-orphan")