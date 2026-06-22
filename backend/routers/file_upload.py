from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import UploadedFile, Session as DBSession
from database.config import get_db
from backend.services.auth import get_current_user
from backend.services.file_upload_service import save_file_to_disk, create_file, get_file_by_id, list_all_files, update_file, delete_file

router = APIRouter(prefix="/file_upload", tags=["File Upload"])

# Pydantic schemas
class UploadedFileBase(BaseModel):
    session_id: UUID
    filename: str
    file_path: str
    file_size: int
    uploaded_at: datetime

class UploadedFileCreate(BaseModel):
    session_id: UUID
    filename: str
    file_size: int

class UploadedFileResponse(UploadedFileBase):
    id: UUID

# Routes
@router.post("/", response_model=UploadedFileResponse)
async def upload_file(
    file: UploadFile = File(...),
    session_id: UUID = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload an Excel file and save its metadata to the database.
    """
    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed.")

    # Save file to disk
    file_path = save_file_to_disk(file, destination=f"uploads/{file.filename}")

    # Create file metadata in the database
    uploaded_file = create_file(
        db=db,
        session_id=session_id,
        filename=file.filename,
        file_path=file_path,
        file_size=file.spool_max_size,
        uploaded_at=datetime.utcnow(),
    )

    return UploadedFileResponse(
        id=uploaded_file.id,
        session_id=uploaded_file.session_id,
        filename=uploaded_file.filename,
        file_path=uploaded_file.file_path,
        file_size=uploaded_file.file_size,
        uploaded_at=uploaded_file.uploaded_at,
    )

@router.get("/", response_model=List[UploadedFileResponse])
async def list_files(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    List all uploaded files.
    """
    files = list_all_files(db)
    return [
        UploadedFileResponse(
            id=file.id,
            session_id=file.session_id,
            filename=file.filename,
            file_path=file.file_path,
            file_size=file.file_size,
            uploaded_at=file.uploaded_at,
        )
        for file in files
    ]

@router.get("/{file_id}", response_model=UploadedFileResponse)
async def get_file(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get details of a specific uploaded file by ID.
    """
    file = get_file_by_id(db, file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found.")

    return UploadedFileResponse(
        id=file.id,
        session_id=file.session_id,
        filename=file.filename,
        file_path=file.file_path,
        file_size=file.file_size,
        uploaded_at=file.uploaded_at,
    )

@router.put("/{file_id}", response_model=UploadedFileResponse)
async def update_file_metadata(
    file_id: UUID,
    file_update: UploadedFileCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update metadata of an uploaded file.
    """
    updated_file = update_file(db, file_id, file_update)
    if not updated_file:
        raise HTTPException(status_code=404, detail="File not found.")

    return UploadedFileResponse(
        id=updated_file.id,
        session_id=updated_file.session_id,
        filename=updated_file.filename,
        file_path=updated_file.file_path,
        file_size=updated_file.file_size,
        uploaded_at=updated_file.uploaded_at,
    )

@router.delete("/{file_id}", response_model=dict)
async def delete_file_endpoint(
    file_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete an uploaded file by ID.
    """
    success = delete_file(db, file_id)
    if not success:
        raise HTTPException(status_code=404, detail="File not found.")

    return {"detail": "File deleted successfully."}