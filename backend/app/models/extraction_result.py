from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from .base import Base
from sqlalchemy.orm import relationship


class ExtractionResult(Base):
    __tablename__ = "extraction_results"

    id = Column(Integer, primary_key= True, index = True)
    studio_id = Column(Integer, ForeignKey("prompt_studios.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(Integer, ForeignKey("extraction_documents.id", ondelete="CASCADE"), nullable=True)
    extracted_data = Column(JSON, nullable=False)
    usage = Column(JSON, nullable=False)
    raw_output = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    studio = relationship("PromptStudio", back_populates="extraction_results")
    document = relationship("ExtractionDocument", back_populates="extraction_results")


