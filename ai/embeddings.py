import os
from typing import List
import openai

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

class EmbeddingClient:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        openai.api_key = self.api_key

    def embed_text(self, text: str) -> List[float]:
        response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        embedding = response['data'][0]['embedding']
        if len(embedding) != EMBEDDING_DIM:
            raise ValueError(f"Embedding dimension mismatch. Expected {EMBEDDING_DIM}, got {len(embedding)}.")
        return embedding

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        response = openai.Embedding.create(
            model=EMBEDDING_MODEL,
            input=texts
        )
        embeddings = [item['embedding'] for item in response['data']]
        for embedding in embeddings:
            if len(embedding) != EMBEDDING_DIM:
                raise ValueError(f"Embedding dimension mismatch. Expected {EMBEDDING_DIM}, got {len(embedding)}.")
        return embeddings

def get_embedding(texts: List[str]) -> List[List[float]]:
    client = EmbeddingClient()
    return client.embed_batch(texts)