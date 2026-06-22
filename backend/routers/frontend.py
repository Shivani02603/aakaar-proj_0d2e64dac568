from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import User, Session, UploadedFile, Message
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(prefix="/frontend", tags=["Frontend"])

# Pydantic Schemas
class FileUploadRequest(BaseModel):
    session_id: UUID
    filename: str
    file_path: str
    file_size: int

class FileUploadResponse(BaseModel):
    id: UUID
    session_id: UUID
    filename: str
    file_path: str
    file_size: int
    uploaded_at: datetime

class SessionRequest(BaseModel):
    name: str

class SessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    created_at: datetime

class MessageRequest(BaseModel):
    session_id: UUID
    role: str
    content: str
    citations: Optional[dict] = None

class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    citations: Optional[dict] = None
    created_at: datetime

# Routes
@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    session_request: SessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_session = Session(
        user_id=current_user.id,
        name=session_request.name,
        created_at=datetime.utcnow(),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sessions = db.query(Session).filter(Session.user_id == current_user.id).all()
    return sessions


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID = Path(..., description="The ID of the session to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(Session).filter(Session.id == session_id, Session.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(
    session_id: UUID = Path(..., description="The ID of the session to delete"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(Session).filter(Session.id == session_id, Session.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()


@router.post("/files/upload", response_model=FileUploadResponse)
async def upload_file(
    file_upload_request: FileUploadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(Session).filter(Session.id == file_upload_request.session_id, Session.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    new_file = UploadedFile(
        session_id=file_upload_request.session_id,
        filename=file_upload_request.filename,
        file_path=file_upload_request.file_path,
        file_size=file_upload_request.file_size,
        uploaded_at=datetime.utcnow(),
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file


@router.get("/sessions/{session_id}/files", response_model=List[FileUploadResponse])
async def list_session_files(
    session_id: UUID = Path(..., description="The ID of the session to list files for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(Session).filter(Session.id == session_id, Session.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    files = db.query(UploadedFile).filter(UploadedFile.session_id == session_id).all()
    return files


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: UUID = Path(..., description="The ID of the session to retrieve messages for"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(Session).filter(Session.id == session_id, Session.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    messages = db.query(Message).filter(Message.session_id == session_id).all()
    return messages


@router.post("/messages", response_model=MessageResponse)
async def create_message(
    message_request: MessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.query(Session).filter(Session.id == message_request.session_id, Session.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    new_message = Message(
        session_id=message_request.session_id,
        role=message_request.role,
        content=message_request.content,
        citations=message_request.citations,
        created_at=datetime.utcnow(),
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message