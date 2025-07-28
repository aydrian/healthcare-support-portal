import sys
from pathlib import Path

# Add the common package to Python path
common_path = Path(__file__).parent.parent.parent.parent.parent / "common" / "src"
sys.path.insert(0, str(common_path))

from typing import List, Optional
import numpy as np
import openai
from sqlalchemy.orm import Session
from sqlalchemy import text

from common.models import Document, Embedding

async def generate_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Generate embedding for a given text using OpenAI."""
    try:
        client = openai.OpenAI()
        response = client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

async def store_document_embeddings(
    document: Document,
    chunks: List[str],
    db: Session,
    model: str = "text-embedding-3-small"
) -> bool:
    """Generate and store embeddings for document chunks."""
    try:
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding_vector = await generate_embedding(chunk, model)

            if not embedding_vector:
                continue

            # Create embedding record
            db_embedding = Embedding(
                document_id=document.id,
                content_chunk=chunk,
                embedding_vector=embedding_vector,
                chunk_index=i
            )

            db.add(db_embedding)

        db.commit()
        return True

    except Exception as e:
        print(f"Error storing embeddings: {e}")
        db.rollback()
        return False

async def similarity_search(
    query_text: str,
    db: Session,
    limit: int = 5,
    similarity_threshold: float = 0.7,
    document_ids: Optional[List[int]] = None
) -> List[dict]:
    """
    Perform similarity search using pgvector.
    """
    try:
        # Generate query embedding
        query_embedding = await generate_embedding(query_text)

        if not query_embedding:
            return []

        # Build SQL query for similarity search
        base_query = """
        SELECT 
            e.id,
            e.document_id,
            e.content_chunk,
            e.chunk_index,
            d.title,
            d.document_type,
            d.department,
            d.is_sensitive,
            1 - (e.embedding_vector <=> %s::vector) as similarity
        FROM embeddings e
        JOIN documents d ON e.document_id = d.id
        WHERE 1 - (e.embedding_vector <=> %s::vector) > %s
        """

        params = [query_embedding, query_embedding, similarity_threshold]

        # Add document ID filter if provided
        if document_ids:
            placeholders = ','.join(['%s'] * len(document_ids))
            base_query += f" AND e.document_id IN ({placeholders})"
            params.extend(document_ids)

        base_query += " ORDER BY similarity DESC LIMIT %s"
        params.append(limit)

        # Execute query
        result = db.execute(text(base_query), params)
        rows = result.fetchall()

        # Convert to list of dictionaries
        results = []
        for row in rows:
            results.append({
                "embedding_id": row[0],
                "document_id": row[1],
                "content_chunk": row[2],
                "chunk_index": row[3],
                "document_title": row[4],
                "document_type": row[5],
                "department": row[6],
                "is_sensitive": row[7],
                "similarity": float(row[8])
            })

        return results

    except Exception as e:
        print(f"Error in similarity search: {e}")
        return []

def combine_chunks_for_context(search_results: List[dict], max_tokens: int = 6000) -> str:
    """
    Combine relevant chunks into context for RAG, respecting token limits.
    """
    context_parts = []
    current_tokens = 0

    for result in search_results:
        chunk = result["content_chunk"]
        title = result["document_title"]

        # Simple token estimation (more accurate would use tiktoken)
        chunk_tokens = len(chunk.split()) * 1.3  # Rough estimation

        if current_tokens + chunk_tokens > max_tokens:
            break

        context_part = f"Document: {title}\nContent: {chunk}\n---\n"
        context_parts.append(context_part)
        current_tokens += chunk_tokens

    return "\n".join(context_parts)
