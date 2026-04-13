from pydantic import BaseModel
from typing import Optional

class PromptCreate(BaseModel):
    field_name: str
    prompt_text: str
    studio_id: int

class PromptUpdate(BaseModel):
    field_name: Optional[str] = None
    prompt_text: Optional[str] = None

class PromptOut(BaseModel):
    id: int
    field_name: str
    prompt_text: str
    studio_id: int

    class Config:
        from_attributes = True