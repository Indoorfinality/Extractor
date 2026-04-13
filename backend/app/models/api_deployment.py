from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from .base import Base
from sqlalchemy.orm import relationship

class ApiDeployment(Base):
    __tablename__ = "api_deployments"

    id = Column(Integer, primary_key=True, index=True)
    studio_id = Column(Integer, ForeignKey("prompt_studios.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), unique = True, nullable=False)
    endpoint_url = Column(String(255), nullable=False)
    api_key = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    studio = relationship("PromptStudio", back_populates="api_deployments")

    