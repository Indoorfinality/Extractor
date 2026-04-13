from sqlalchemy import Column, Integer, String,Text, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class FieldPrompt(Base):
    __tablename__ = "field_prompts"

    id = Column(Integer, primary_key=True, index=True)
    field_name = Column(String(100), nullable=False)
    prompt_text = Column(Text, nullable=False)
    studio_id = Column(Integer, ForeignKey("prompt_studios.id"), nullable=False)

    studio = relationship("PromptStudio", back_populates="prompts")