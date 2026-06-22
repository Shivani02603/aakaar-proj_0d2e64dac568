import os
import psycopg2
from typing import List, Dict, Any

class VectorStore:
    def __init__(self):
        self.connection = None

    def _connect(self):
        if not self.connection:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                raise ValueError("DATABASE_URL environment variable is not set.")
            self.connection = psycopg2.connect(db_url)

    def upsert(self, id: str, vector: List[float], metadata: Dict[str, Any]):
        self._connect()
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO vectors (id, embedding, metadata)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata;
            """, (id, vector, metadata))
            self.connection.commit()

    def search(self, query_embedding: List[float], top_k: int, **filters) -> List[Dict[str, Any]]:
        self._connect()
        filter_conditions = " AND ".join([f"{key} = %s" for key in filters.keys()])
        filter_values = list(filters.values())
        query = f"""
            SELECT id, embedding, metadata, 1 - (embedding <=> %s) AS similarity
            FROM vectors
            {"WHERE " + filter_conditions if filters else ""}
            ORDER BY similarity DESC
            LIMIT %s;
        """
        with self.connection.cursor() as cursor:
            cursor.execute(query, [query_embedding] + filter_values + [top_k])
            results = cursor.fetchall()
        return [
            {"id": row[0], "embedding": row[1], "metadata": row[2], "similarity": row[3]}
            for row in results
        ]