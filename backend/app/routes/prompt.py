from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..dependencies import get_db
from ..models.field_prompt import FieldPrompt
from ..models.prompt_studio import PromptStudio
from ..schemas.prompt import PromptCreate, PromptOut, PromptUpdate

router = APIRouter()

@router.post("/", response_model=PromptOut, status_code=status.HTTP_201_CREATED)
def create_prompt(prompt_data: PromptCreate, db: Session = Depends(get_db)):
    studio = db.query(PromptStudio).filter(PromptStudio.id == prompt_data.studio_id).first()
    if not studio:
        raise HTTPException(404, "Studio not found")

    existing = db.query(FieldPrompt).filter(
        FieldPrompt.field_name == prompt_data.field_name,
        FieldPrompt.studio_id == prompt_data.studio_id
    ).first()
    if existing:
        raise HTTPException(400, "Field already exists in this studio")
    

    new_prompt = FieldPrompt(**prompt_data.model_dump())
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return new_prompt

@router.get("/{studio_id}", response_model=List[PromptOut])
def list_prompts(studio_id: int, db: Session = Depends(get_db)):
    studio = db.query(PromptStudio).filter(PromptStudio.id == studio_id).first()
    if not studio:
        raise HTTPException(404, "Studio not found")
    return db.query(FieldPrompt).filter(FieldPrompt.studio_id == studio_id).all()


@router.put("/{prompt_id}", response_model=PromptOut)
def update_prompt(prompt_id: int, prompt_data: PromptUpdate, db: Session = Depends(get_db)):
    db_prompt = db.query(FieldPrompt).filter(FieldPrompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(404, "Prompt not found")
    update_data = prompt_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_prompt, key, value)

    db.commit()
    db.refresh(db_prompt)
    return db_prompt

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    db_prompt = db.query(FieldPrompt).filter(FieldPrompt.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(404, "Prompt not found")
    db.delete(db_prompt)
    db.commit()
    return None
    
