from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models import DocumentChunk, UploadedFile
from datetime import datetime
import pandas as pd
from ai.embeddings import get_embedding

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

class IngestionPipelineService:
    async def create_chunks_from_file(self, uploaded_file_id: UUID, db: AsyncSession) -> List[DocumentChunk]:
        try:
            # Fetch the uploaded file record
            result = await db.execute(select(UploadedFile).where(UploadedFile.id == uploaded_file_id))
            uploaded_file = result.scalar_one_or_none()
            if not uploaded_file:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uploaded file not found")

            # Parse the Excel file
            try:
                excel_data = pd.ExcelFile(uploaded_file.file_path)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error parsing Excel file: {str(e)}")

            chunks = []
            for sheet_name in excel_data.sheet_names:
                sheet_data = excel_data.parse(sheet_name)
                content = sheet_data.to_string(index=False, header=False)

                # Split content into overlapping chunks
                tokens = content.split()
                for i in range(0, len(tokens), CHUNK_SIZE - CHUNK_OVERLAP):
                    chunk_tokens = tokens[i:i + CHUNK_SIZE]
                    chunk_content = " ".join(chunk_tokens)
                    chunk_index = len(chunks)

                    # Generate embedding for the chunk
                    embedding = get_embedding([chunk_content])[0]

                    # Create DocumentChunk instance
                    chunk = DocumentChunk(
                        uploaded_file_id=uploaded_file_id,
                        content=chunk_content,
                        chunk_index=chunk_index,
                        start_row=i,
                        end_row=min(i + CHUNK_SIZE, len(tokens)),
                        sheet_name=sheet_name,
                        embedding=embedding,
                        created_at=datetime.utcnow()
                    )
                    db.add(chunk)
                    chunks.append(chunk)

            await db.commit()
            return chunks
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")

    async def get_chunk_by_id(self, chunk_id: UUID, db: AsyncSession) -> DocumentChunk:
        try:
            result = await db.execute(select(DocumentChunk).where(DocumentChunk.id == chunk_id))
            chunk = result.scalar_one_or_none()
            if not chunk:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")
            return chunk
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching chunk: {str(e)}")

    async def list_all_chunks(self, uploaded_file_id: UUID, db: AsyncSession) -> List[DocumentChunk]:
        try:
            result = await db.execute(select(DocumentChunk).where(DocumentChunk.uploaded_file_id == uploaded_file_id))
            chunks = result.scalars().all()
            return chunks
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error listing chunks: {str(e)}")

    async def update_chunk(self, chunk_id: UUID, updated_data: dict, db: AsyncSession) -> DocumentChunk:
        try:
            result = await db.execute(select(DocumentChunk).where(DocumentChunk.id == chunk_id))
            chunk = result.scalar_one_or_none()
            if not chunk:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")

            for key, value in updated_data.items():
                setattr(chunk, key, value)

            chunk.updated_at = datetime.utcnow()
            db.add(chunk)
            await db.commit()
            return chunk
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")

    async def delete_chunk(self, chunk_id: UUID, db: AsyncSession) -> None:
        try:
            result = await db.execute(select(DocumentChunk).where(DocumentChunk.id == chunk_id))
            chunk = result.scalar_one_or_none()
            if not chunk:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document chunk not found")

            await db.delete(chunk)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting chunk: {str(e)}")