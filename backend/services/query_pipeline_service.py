from uuid import UUID
from typing import List, Dict, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from database.models import DocumentChunk, UploadedFile
from ai.embeddings import get_embedding
from ai.rag import retrieve_context
from ai.streaming import stream_answer
from datetime import datetime

class QueryPipelineService:
    async def embed_user_query(self, query: str) -> List[float]:
        """
        Embed the user's query using the embedding client.
        """
        try:
            embedding = get_embedding([query])
            return embedding[0]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to embed query: {str(e)}"
            )

    async def retrieve_top_chunks(self, query_embedding: List[float], session_id: UUID, db: AsyncSession) -> List[DocumentChunk]:
        """
        Retrieve the top-5 chunks based on cosine similarity using pgvector.
        """
        try:
            query = select(DocumentChunk).where(DocumentChunk.session_id == session_id).order_by(
                DocumentChunk.embedding.cosine_similarity(query_embedding).desc()
            ).limit(5)
            result = await db.execute(query)
            chunks = result.scalars().all()
            if not chunks:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No relevant chunks found for the query."
                )
            return chunks
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve top chunks: {str(e)}"
            )

    async def generate_answer_with_context(self, question: str, context: List[DocumentChunk]) -> Dict[str, str]:
        """
        Generate an answer using the Google Generative AI SDK (gemini-2.0-flash).
        """
        try:
            context_text = "\n".join([chunk.content for chunk in context])
            answer = await stream_answer(question, context_text)
            return answer
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate answer: {str(e)}"
            )

    async def query_pipeline(self, question: str, session_id: UUID, db: AsyncSession) -> Dict[str, Optional[str]]:
        """
        Execute the full query pipeline: embed query, retrieve context, generate answer, and return citations.
        """
        try:
            # Step 1: Embed the user's query
            query_embedding = await self.embed_user_query(question)

            # Step 2: Retrieve top-5 relevant chunks
            chunks = await self.retrieve_top_chunks(query_embedding, session_id, db)

            # Step 3: Generate answer using the retrieved context
            answer = await self.generate_answer_with_context(question, chunks)

            # Step 4: Prepare citations
            citations = [
                {
                    "filename": chunk.sheet_name,
                    "row_range": f"{chunk.start_row}-{chunk.end_row}"
                }
                for chunk in chunks
            ]

            return {
                "answer": answer.get("answer"),
                "citations": citations
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to execute query pipeline: {str(e)}"
            )

    async def create_chunks_from_file(self, uploaded_file_id: UUID, db: AsyncSession) -> List[DocumentChunk]:
        """
        Create document chunks from an uploaded file.
        """
        try:
            query = select(UploadedFile).where(UploadedFile.id == uploaded_file_id)
            result = await db.execute(query)
            uploaded_file = result.scalar_one_or_none()
            if not uploaded_file:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Uploaded file not found."
                )

            # Chunk the document
            chunks = chunk(uploaded_file.file_path)
            document_chunks = []
            for idx, chunk_data in enumerate(chunks):
                document_chunk = DocumentChunk(
                    uploaded_file_id=uploaded_file_id,
                    content=chunk_data["content"],
                    chunk_index=idx,
                    start_row=chunk_data["start_row"],
                    end_row=chunk_data["end_row"],
                    sheet_name=chunk_data["sheet_name"],
                    embedding=chunk_data["embedding"],
                    created_at=datetime.utcnow()
                )
                db.add(document_chunk)
                document_chunks.append(document_chunk)

            await db.commit()
            return document_chunks
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create chunks: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create chunks: {str(e)}"
            )

    async def get_chunk_by_id(self, chunk_id: UUID, db: AsyncSession) -> DocumentChunk:
        """
        Retrieve a document chunk by its ID.
        """
        try:
            query = select(DocumentChunk).where(DocumentChunk.id == chunk_id)
            result = await db.execute(query)
            chunk = result.scalar_one_or_none()
            if not chunk:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document chunk not found."
                )
            return chunk
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve chunk: {str(e)}"
            )

    async def list_all_chunks(self, db: AsyncSession) -> List[DocumentChunk]:
        """
        List all document chunks.
        """
        try:
            query = select(DocumentChunk)
            result = await db.execute(query)
            chunks = result.scalars().all()
            return chunks
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list chunks: {str(e)}"
            )

    async def update_chunk(self, chunk_id: UUID, updated_data: Dict[str, str], db: AsyncSession) -> DocumentChunk:
        """
        Update a document chunk.
        """
        try:
            query = select(DocumentChunk).where(DocumentChunk.id == chunk_id)
            result = await db.execute(query)
            chunk = result.scalar_one_or_none()
            if not chunk:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document chunk not found."
                )

            for key, value in updated_data.items():
                setattr(chunk, key, value)

            db.add(chunk)
            await db.commit()
            return chunk
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to update chunk: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update chunk: {str(e)}"
            )

    async def delete_chunk(self, chunk_id: UUID, db: AsyncSession) -> None:
        """
        Delete a document chunk.
        """
        try:
            query = select(DocumentChunk).where(DocumentChunk.id == chunk_id)
            result = await db.execute(query)
            chunk = result.scalar_one_or_none()
            if not chunk:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document chunk not found."
                )

            await db.delete(chunk)
            await db.commit()
        except HTTPException as e:
            raise e
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to delete chunk: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete chunk: {str(e)}"
            )