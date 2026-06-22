from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from database.models import DocumentChunk, UploadedFile, Session, Message
from database.config import get_db
from backend.services.auth import get_current_user
from ai.embeddings import get_embedding
from ai.rag import retrieve_context
from ai.routes import answer_question

router = APIRouter(prefix="/query_pipeline", tags=["Query Pipeline"])

# Pydantic schemas
class QueryRequest(BaseModel):
    question: str = Field(..., description="User's question")
    session_id: UUID = Field(..., description="Session ID")

class Citation(BaseModel):
    filename: str = Field(..., description="Source file name")
    row_range: str = Field(..., description="Row range in the source file")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    citations: List[Citation] = Field(..., description="Source citations")

# Route handlers
@router.post("/query", response_model=QueryResponse)
async def query_pipeline(
    query_request: QueryRequest,
    db: Session = Depends(get_db),
    current_user: Session = Depends(get_current_user),
):
    """
    Handles user queries by embedding the question, retrieving relevant chunks, and generating an answer.
    """
    try:
        # Step 1: Embed the user's query
        embeddings = get_embedding([query_request.question])
        if not embeddings or len(embeddings) == 0:
            raise HTTPException(status_code=500, detail="Failed to generate embeddings for the query.")

        # Step 2: Retrieve top-5 chunks by cosine similarity
        top_chunks = retrieve_context(
            query=embeddings[0],
            top_k=5,
            session_id=query_request.session_id,
            user_id=current_user.id,
        )
        if not top_chunks or len(top_chunks) == 0:
            raise HTTPException(status_code=404, detail="No relevant context found for the query.")

        # Step 3: Pass the retrieved context and user's question to the generative AI model
        context = "\n".join([chunk.content for chunk in top_chunks])
        answer = await answer_question(query_request.question, context)
        if not answer:
            raise HTTPException(status_code=500, detail="Failed to generate an answer.")

        # Step 4: Prepare citations
        citations = [
            Citation(
                filename=chunk.uploaded_file.filename,
                row_range=f"{chunk.start_row}-{chunk.end_row}"
            )
            for chunk in top_chunks
        ]

        # Step 5: Return the generated answer and citations
        return QueryResponse(answer=answer, citations=citations)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))