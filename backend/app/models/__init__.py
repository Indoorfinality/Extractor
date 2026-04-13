"""
Import all SQLAlchemy models so Base.metadata is fully populated at runtime.

This avoids mapper/ForeignKey resolution errors when only a subset of models
are imported by route modules.
"""

from .users import User  
from .prompt_studio import PromptStudio  
from .field_prompt import FieldPrompt 
from .extraction_document import ExtractionDocument  
from .extraction_result import ExtractionResult  
from .api_deployment import ApiDeployment  
