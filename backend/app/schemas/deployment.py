from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DeploymentCreate(BaseModel):
    name: str


class DeploymentOut(BaseModel):
    id: int
    studio_id: int
    name: str
    endpoint_url: str
    api_key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DeploymentOutFull(DeploymentOut):
    studio_name: str

    class Config:
        from_attributes = True


class DeploymentToggle(BaseModel):
    is_active: bool
