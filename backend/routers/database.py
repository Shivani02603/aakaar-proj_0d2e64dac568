from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import User, Session as DBSession, UploadedFile, DocumentChunk, Message
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(prefix="/database", tags=["Database"])

# Pydantic Schemas
class UserBase(BaseModel):
    session_id: str
    created_at: datetime

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID

class SessionBase(BaseModel):
    user_id: UUID
    name: str
    created_at: datetime

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: UUID

class UploadedFileBase(BaseModel):
    session_id: UUID
    filename: str
    file_path: str
    file_size: int
    uploaded_at: datetime

class UploadedFileCreate(UploadedFileBase):
    pass

class UploadedFileResponse(UploadedFileBase):
    id: UUID

class DocumentChunkBase(BaseModel):
    uploaded_file_id: UUID
    content: str
    chunk_index: int
    start_row: int
    end_row: int
    sheet_name: str
    embedding: List[float]
    created_at: datetime

class DocumentChunkCreate(DocumentChunkBase):
    pass

class DocumentChunkResponse(DocumentChunkBase):
    id: UUID

class MessageBase(BaseModel):
    session_id: UUID
    role: str
    content: str
    citations: dict
    created_at: datetime

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: UUID

# CRUD Endpoints for User
@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: UUID, user_update: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user_update.dict().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

# CRUD Endpoints for Session
@router.get("/sessions", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = db.query(DBSession).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/sessions", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_session = DBSession(**session.dict())
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.put("/sessions/{session_id}", response_model=SessionResponse)
def update_session(session_id: UUID, session_update: SessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    for key, value in session_update.dict().items():
        setattr(session, key, value)
    db.commit()
    db.refresh(session)
    return session

@router.delete("/sessions/{session_id}", response_model=dict)
def delete_session(session_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"detail": "Session deleted successfully"}