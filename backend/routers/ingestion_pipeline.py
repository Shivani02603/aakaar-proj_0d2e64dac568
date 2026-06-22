from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import DocumentChunk, UploadedFile
from database.config import get_db
from backend.services.auth import get_current_user
from ai.embeddings import get_embedding
import pandas as pd
import os
from pathlib import Path

router = APIRouter(prefix="/ingestion_pipeline", tags=["Ingestion Pipeline"])

# Pydantic schemas
class DocumentChunkBase(BaseModel):
    uploaded_file_id: UUID
    content: str
    chunk_index: int
    start_row: int
    end_row: int
    sheet_name: str
    embedding: List[float]

class DocumentChunkCreate(DocumentChunkBase):
    pass

class DocumentChunkResponse(DocumentChunkBase):
    id: UUID
    created_at: datetime

class UploadedFileResponse(BaseModel):
    id: UUID
    session_id: UUID
    filename: str
    file_path: str
    file_size: int
    uploaded_at: datetime

# Helper functions
def parse_excel(file_path: str) -> List[dict]:
    try:
        parsed_data = []
        excel_data = pd.ExcelFile(file_path)
        for sheet_name in excel_data.sheet_names:
            sheet_data = excel_data.parse(sheet_name)
            for index, row in sheet_data.iterrows():
                parsed_data.append({
                    "sheet_name": sheet_name,
                    "row_index": index,
                    "content": row.to_dict()
                })
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing Excel file: {str(e)}")

def split_into_chunks(parsed_data: List[dict], chunk_size: int = 1000, overlap: int = 200) -> List[List[dict]]:
    chunks = []
    for i in range(0, len(parsed_data), chunk_size - overlap):
        chunks.append(parsed_data[i:i + chunk_size])
    return chunks

# Routes
@router.post("/ingest", response_model=List[DocumentChunkResponse])
async def ingest_file(
    file: UploadFile = File(...),
    session_id: UUID = Form(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Save file to disk
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Parse Excel file
        parsed_data = parse_excel(str(file_path))

        # Split into chunks
        chunks = split_into_chunks(parsed_data)

        # Embed chunks and store in database
        document_chunks = []
        for chunk_index, chunk in enumerate(chunks):
            content = " ".join([str(row["content"]) for row in chunk])
            embedding = get_embedding([content])[0]
            start_row = chunk[0]["row_index"]
            end_row = chunk[-1]["row_index"]
            sheet_name = chunk[0]["sheet_name"]

            document_chunk = DocumentChunk(
                uploaded_file_id=session_id,
                content=content,
                chunk_index=chunk_index,
                start_row=start_row,
                end_row=end_row,
                sheet_name=sheet_name,
                embedding=embedding,
                created_at=datetime.utcnow()
            )
            db.add(document_chunk)
            document_chunks.append(document_chunk)

        db.commit()

        # Return response
        return [DocumentChunkResponse(
            id=chunk.id,
            uploaded_file_id=chunk.uploaded_file_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            start_row=chunk.start_row,
            end_row=chunk.end_row,
            sheet_name=chunk.sheet_name,
            embedding=chunk.embedding,
            created_at=chunk.created_at
        ) for chunk in document_chunks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during ingestion: {str(e)}")

@router.get("/chunks", response_model=List[DocumentChunkResponse])
async def list_chunks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        chunks = db.query(DocumentChunk).all()
        return [DocumentChunkResponse(
            id=chunk.id,
            uploaded_file_id=chunk.uploaded_file_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            start_row=chunk.start_row,
            end_row=chunk.end_row,
            sheet_name=chunk.sheet_name,
            embedding=chunk.embedding,
            created_at=chunk.created_at
        ) for chunk in chunks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chunks: {str(e)}")

@router.get("/chunks/{chunk_id}", response_model=DocumentChunkResponse)
async def get_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        return DocumentChunkResponse(
            id=chunk.id,
            uploaded_file_id=chunk.uploaded_file_id,
            content=chunk.content,
            chunk_index=chunk.chunk_index,
            start_row=chunk.start_row,
            end_row=chunk.end_row,
            sheet_name=chunk.sheet_name,
            embedding=chunk.embedding,
            created_at=chunk.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chunk: {str(e)}")

@router.delete("/chunks/{chunk_id}")
async def delete_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()
        if not chunk:
            raise HTTPException(status_code=404, detail="Chunk not found")
        db.delete(chunk)
        db.commit()
        return {"detail": "Chunk deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting chunk: {str(e)}")