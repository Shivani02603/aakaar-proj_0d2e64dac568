from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=True)
    created_at = Column(DateTime, nullable=False)

class Session(Base):
    __tablename__ = 'sessions'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

class UploadedFile(Base):
    __tablename__ = 'uploaded_files'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Float, nullable=False)
    uploaded_at = Column(DateTime, nullable=False)

class DocumentChunk(Base):
    __tablename__ = 'document_chunks'
    id = Column(Integer, primary_key=True, index=True)
    uploaded_file_id = Column(Integer, ForeignKey('uploaded_files.id'), nullable=False)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    start_row = Column(Integer, nullable=False)
    end_row = Column(Integer, nullable=False)
    sheet_name = Column(String, nullable=True)
    embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False)

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey('sessions.id'), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False)