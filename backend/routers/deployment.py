from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import Deployment
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(prefix="/deployment", tags=["Deployment"])

# Pydantic schemas
class DeploymentBase(BaseModel):
    name: str = Field(..., example="My Deployment")
    description: Optional[str] = Field(None, example="Deployment description")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class DeploymentCreate(DeploymentBase):
    pass

class DeploymentUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Updated Deployment Name")
    description: Optional[str] = Field(None, example="Updated Deployment description")

class DeploymentResponse(DeploymentBase):
    id: UUID

# CRUD endpoints
@router.post("/", response_model=DeploymentResponse, status_code=201)
async def create_deployment(
    deployment: DeploymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    new_deployment = Deployment(**deployment.dict())
    db.add(new_deployment)
    db.commit()
    db.refresh(new_deployment)
    return new_deployment

@router.get("/", response_model=List[DeploymentResponse])
async def list_deployments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    deployments = db.query(Deployment).all()
    return deployments

@router.get("/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    deployment_id: UUID = Path(..., description="The ID of the deployment to retrieve"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment

@router.put("/{deployment_id}", response_model=DeploymentResponse)
async def update_deployment(
    deployment_update: DeploymentUpdate,
    deployment_id: UUID = Path(..., description="The ID of the deployment to update"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    for key, value in deployment_update.dict(exclude_unset=True).items():
        setattr(deployment, key, value)
    
    db.commit()
    db.refresh(deployment)
    return deployment

@router.delete("/{deployment_id}", status_code=204)
async def delete_deployment(
    deployment_id: UUID = Path(..., description="The ID of the deployment to delete"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    deployment = db.query(Deployment).filter(Deployment.id == deployment_id).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    db.delete(deployment)
    db.commit()
    return None