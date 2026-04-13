from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..dependencies import get_db
from ..models.prompt_studio import PromptStudio
from ..schemas.studio import StudioCreate, StudioOut, StudioUpdate


router = APIRouter()
@router.post("/", response_model =StudioOut, status_code = status.HTTP_201_CREATED)
def create_studio(studio: StudioCreate, db: Session = Depends(get_db)):
    fake_user_id = 1
    db_studio = PromptStudio(**studio.model_dump(),
                             user_id=fake_user_id)
    db.add(db_studio)
    db.commit()
    db.refresh(db_studio)
    return db_studio

@router.get("/", response_model = List[StudioOut])
def list_studios(db: Session = Depends(get_db)):
    fake_user_id = 1
    return db.query(PromptStudio).filter(PromptStudio.user_id == fake_user_id).all()

@router.put("/{studio_id}", response_model=StudioOut)
def update_studio(studio_id: int, studio:StudioUpdate, db: Session = Depends(get_db)):
    fake_user_id = 1
    db_studio = db.query(PromptStudio).filter(
        PromptStudio.id == studio_id,
        PromptStudio.user_id == fake_user_id
    ).first()

    if db_studio is None:
        raise HTTPException(404, "Studio not found")
    
    update_data = studio.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_studio, key, value)
    db.commit()
    db.refresh(db_studio)
    return db_studio

@router.delete("/{studio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_studio(studio_id: int, db: Session = Depends(get_db)):
    fake_user_id = 1
    db_studio = db.query(PromptStudio).filter(
        PromptStudio.id == studio_id,
        PromptStudio.user_id == fake_user_id
    ).first()
  
    if not db_studio:
        raise HTTPException(404, "Studio not found")

    db.delete(db_studio)
    db.commit()
    return None








