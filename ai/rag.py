import os
from pgvector.psycopg2 import Vector
import psycopg2
import google.generativeai as genai

def retrieve_context(query, top_k, session_id, user_id):
    """
    Embeds the query, retrieves the top-k relevant chunks from the vector store.
    """
    # Read the PostgreSQL connection details from environment variables
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    if not all([db_host, db_port, db_name, db_user, db_password]):
        raise ValueError("Database connection details are not fully set in environment variables.")

    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    cursor = conn.cursor()

    # Generate embedding for the query
    query_embedding = generate_embedding(query)

    # Retrieve top-k chunks by cosine similarity
    cursor.execute(
        """
        SELECT chunk_text
        FROM vector_store
        WHERE session_id = %s AND user_id = %s
        ORDER BY embedding <=> %s
        LIMIT %s;
        """,
        (session_id, user_id, Vector(query_embedding), top_k)
    )
    results = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()

    # Extract chunk texts
    return [row[0] for row in results]

def generate_embedding(text):
    """
    Placeholder function for generating embeddings.
    Replace this with the actual embedding generation logic.
    """
    raise NotImplementedError("Embedding generation function is not implemented.")

def answer_question(query: str, session_id: str, user_id: str) -> dict:
    """
    Retrieves context, builds a prompt, and generates an answer using the runtime LLM.
    """
    # Retrieve the API key for the runtime LLM
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")

    # Retrieve relevant context
    context_chunks = retrieve_context(query, top_k=5, session_id=session_id, user_id=user_id)

    # Build the prompt
    context = "\n".join(context_chunks)
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"

    # Initialize the Gemini API client
    genai.configure(api_key=gemini_api_key)

    # Generate the answer
    response = genai.generate_text(prompt=prompt)

    # Extract the answer and sources
    answer = response.get("text", "").strip()
    sources = context_chunks  # Use the retrieved chunks as sources

    return {"answer": answer, "sources": sources}