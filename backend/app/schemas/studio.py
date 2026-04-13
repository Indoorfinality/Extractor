from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StudioCreate(BaseModel):
    name: str
    description: str | None = None

class StudioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class StudioOut(BaseModel):
    id: int
    name: str
    description: str | None
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
