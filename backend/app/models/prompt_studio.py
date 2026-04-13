from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .base import Base

class PromptStudio(Base):
    __tablename__ = "prompt_studios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    prompts = relationship("FieldPrompt", back_populates="studio", cascade="all, delete-orphan")
    documents = relationship("ExtractionDocument", back_populates="studio", cascade="all, delete-orphan")
    extraction_results = relationship("ExtractionResult", back_populates="studio", cascade="all, delete-orphan")
    api_deployments = relationship("ApiDeployment", back_populates="studio", cascade="all, delete-orphan")