from pydantic import BaseModel
from typing import Dict, Any, List


class ExtractionRunRequest(BaseModel):
    studio_id: int
    document_id: int


class ExtractionRunResponse(BaseModel):
    extracted_fields: Dict[str, Any]
    output_path: str
    usage: Dict[str, Any]
    raw_output: str | None = None
    
    class Config:
        from_attributes = True
