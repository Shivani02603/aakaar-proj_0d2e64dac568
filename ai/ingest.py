import os
import pandas as pd
from pgvector.psycopg2 import Vector
import psycopg2

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def chunk(document):
    """
    Splits a document into overlapping chunks using the recursive strategy.
    """
    chunks = []
    start = 0
    while start < len(document):
        end = min(start + CHUNK_SIZE, len(document))
        chunks.append(document[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks

def get_embedding(text):
    """
    Placeholder function for generating embeddings from text.
    Replace this with the actual implementation.
    """
    # Example: Return a dummy embedding (list of zeros)
    return [0.0] * 768

def ingest_excel(file_path, session_id, user_id):
    """
    Reads an Excel file, chunks its content, generates embeddings, and upserts into the vector store.
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

    # Read the Excel file
    excel_data = pd.ExcelFile(file_path)

    for sheet_name in excel_data.sheet_names:
        sheet_data = excel_data.parse(sheet_name)
        document = sheet_data.to_csv(index=False)  # Convert the sheet to a CSV-like string

        # Chunk the document
        chunks = chunk(document)

        for chunk_text in chunks:
            # Generate embedding for the chunk
            embedding = get_embedding(chunk_text)

            # Upsert into the vector store
            cursor.execute(
                """
                INSERT INTO vector_store (session_id, user_id, chunk_text, embedding)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (session_id, user_id, chunk_text)
                DO UPDATE SET embedding = EXCLUDED.embedding;
                """,
                (session_id, user_id, chunk_text, Vector(embedding))
            )

    # Commit and close the database connection
    conn.commit()
    cursor.close()
    conn.close()