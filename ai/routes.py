from fastapi import APIRouter, UploadFile, Form, Query, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from ai.ingest import ingest_excel
from ai.rag import answer_question
from ai.streaming import stream_answer

router = APIRouter(prefix='/api/ai')

# Request and Response Models
class IngestRequest(BaseModel):
    file: UploadFile

class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    citations: list

# Routes
@router.post("/ingest")
async def ingest(file: UploadFile):
    """
    Endpoint to ingest an Excel file.
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only .xlsx files are supported.")
    try:
        await ingest_excel(file)
        return {"status": "success", "message": "File ingested successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during ingestion: {str(e)}")

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Endpoint to process a user question and return an answer with citations.
    """
    try:
        answer, citations = await answer_question(request.question, request.session_id)
        return {"answer": answer, "citations": citations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during query processing: {str(e)}")

@router.get("/stream")
async def stream(query: str = Query(...), session_id: Optional[str] = Query(None)):
    """
    Endpoint to stream an answer to a user question.
    """
    try:
        return StreamingResponse(stream_answer(query, session_id), media_type='text/event-stream')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during streaming: {str(e)}")