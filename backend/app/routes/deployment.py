from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
import secrets

from ..dependencies import get_db
from ..models.api_deployment import ApiDeployment
from ..schemas.deployment import DeploymentCreate, DeploymentOut, DeploymentOutFull, DeploymentToggle
from ..models.prompt_studio import PromptStudio

router = APIRouter(tags=["deployments"])


@router.post("/", response_model=DeploymentOut, status_code=status.HTTP_201_CREATED)
def create_deployment(
    deployment: DeploymentCreate,
    studio_id: int,
    db: Session = Depends(get_db),
):
    studio = db.query(PromptStudio).filter(PromptStudio.id == studio_id).first()
    if not studio:
        raise HTTPException(status_code=404, detail="Studio not found")

    existing = db.query(ApiDeployment).filter(ApiDeployment.name == deployment.name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"API name '{deployment.name}' already exists. Choose a different name.",
        )

    api_key = f"sk_{secrets.token_hex(32)}"
    endpoint_url = f"/api/extraction/extract/{deployment.name}"

    new_deployment = ApiDeployment(
        studio_id=studio_id,
        name=deployment.name,
        endpoint_url=endpoint_url,
        api_key=api_key,
        is_active=True,
    )
    db.add(new_deployment)
    db.commit()
    db.refresh(new_deployment)
    return new_deployment


@router.get("/{studio_id}", response_model=list[DeploymentOut])
def list_deployments(studio_id: int, db: Session = Depends(get_db)):
    return (
        db.query(ApiDeployment)
        .filter(ApiDeployment.studio_id == studio_id)
        .order_by(ApiDeployment.created_at.desc())
        .all()
    )


@router.get("/", response_model=list[DeploymentOutFull])
def list_all_deployments(db: Session = Depends(get_db)):
    rows = (
        db.query(ApiDeployment, PromptStudio.name.label("studio_name"))
        .join(PromptStudio, PromptStudio.id == ApiDeployment.studio_id)
        .order_by(ApiDeployment.created_at.desc())
        .all()
    )
    results = []
    for dep, studio_name in rows:
        d = DeploymentOutFull(
            id=dep.id,
            studio_id=dep.studio_id,
            name=dep.name,
            endpoint_url=dep.endpoint_url,
            api_key=dep.api_key,
            is_active=dep.is_active,
            created_at=dep.created_at,
            studio_name=studio_name,
        )
        results.append(d)
    return results


@router.patch("/{deployment_id}/toggle", response_model=DeploymentOut)
def toggle_deployment(
    deployment_id: int,
    payload: DeploymentToggle,
    db: Session = Depends(get_db),
):
    dep = db.query(ApiDeployment).filter(ApiDeployment.id == deployment_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    dep.is_active = payload.is_active
    db.commit()
    db.refresh(dep)
    return dep


@router.delete("/{deployment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deployment(deployment_id: int, db: Session = Depends(get_db)):
    dep = db.query(ApiDeployment).filter(ApiDeployment.id == deployment_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    db.delete(dep)
    db.commit()
    return None
