from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentOut(BaseModel):
    id: int
    filename: str
    file_path: str
    studio_id: int
    uploaded_by: int
    size: Optional[int] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True