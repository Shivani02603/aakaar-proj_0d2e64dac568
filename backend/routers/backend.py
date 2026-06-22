from fastapi import APIRouter, Depends, HTTPException, Path, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import User, Session, UploadedFile
from database.config import get_db
from backend.services.auth import get_current_user

router = APIRouter(prefix="/backend", tags=["Backend"])

# Pydantic Schemas
class UserBase(BaseModel):
    session_id: str
    created_at: datetime

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID

class SessionBase(BaseModel):
    name: str
    created_at: datetime

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: UUID
    user_id: UUID

class UploadedFileBase(BaseModel):
    filename: str
    file_path: str
    file_size: int
    uploaded_at: datetime

class UploadedFileCreate(UploadedFileBase):
    session_id: UUID

class UploadedFileResponse(UploadedFileBase):
    id: UUID

# Routes
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
def create_user(user: UserCreate, db: Session = Depends(get_db)):
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

@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None

@router.get("/sessions", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sessions = db.query(Session).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/sessions", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    new_session = Session(**session.dict())
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.put("/sessions/{session_id}", response_model=SessionResponse)
def update_session(session_id: UUID, session_update: SessionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    for key, value in session_update.dict().items():
        setattr(session, key, value)
    db.commit()
    db.refresh(session)
    return session

@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(Session).filter(Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return None

@router.get("/files", response_model=List[UploadedFileResponse])
def list_files(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    files = db.query(UploadedFile).all()
    return files

@router.get("/files/{file_id}", response_model=UploadedFileResponse)
def get_file(file_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@router.post("/files", response_model=UploadedFileResponse)
def create_file(file: UploadedFileCreate, db: Session = Depends(get_db)):
    new_file = UploadedFile(**file.dict())
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    return new_file

@router.put("/files/{file_id}", response_model=UploadedFileResponse)
def update_file(file_id: UUID, file_update: UploadedFileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    for key, value in file_update.dict().items():
        setattr(file, key, value)
    db.commit()
    db.refresh(file)
    return file

@router.delete("/files/{file_id}", status_code=204)
def delete_file(file_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    file = db.query(UploadedFile).filter(UploadedFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    db.delete(file)
    db.commit()
    return None