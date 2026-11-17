"""Embedding service using SentenceTransformers and ChromaDB for vector storage."""

import logging
import os
from typing import Any

import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

# Module-level singletons (lazy loaded)
_model = None
_chroma_client = None
_collection = None


def get_model():
    """Lazy load SentenceTransformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info("Loading SentenceTransformer model 'all-MiniLM-L6-v2'...")
            _model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("SentenceTransformer model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer: {e}")
            raise RuntimeError(f"Embedding model initialization failed: {e}")
    return _model


def get_chroma_collection():
    """Lazy load ChromaDB persistent client and collection."""
    global _chroma_client, _collection
    if _collection is None:
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            persist_dir = settings.CHROMA_PERSIST_DIR
            os.makedirs(persist_dir, exist_ok=True)

            _chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            _collection = _chroma_client.get_or_create_collection(
                name="resumes_and_jds",
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("ChromaDB collection initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise RuntimeError(f"ChromaDB initialization failed: {e}")
    return _collection


def get_embedding(text: str) -> list[float]:
    """Generate dense vector embedding for input text.

    Args:
        text: Input string.

    Returns:
        List of floats representing the embedding vector (384-dim for all-MiniLM-L6-v2).
    """
    if not text or not text.strip():
        # Return zero vector if empty
        return [0.0] * 384
    model = get_model()
    embedding = model.encode(text.strip(), normalize_embeddings=True)
    return embedding.tolist()


def store_embedding(doc_id: str, text: str, metadata: dict[str, Any] | None = None) -> None:
    """Store text and its embedding in ChromaDB vector store.

    Args:
        doc_id: Unique document ID.
        text: Document text to embed and store.
        metadata: Key-value dictionary of metadata.
    """
    collection = get_chroma_collection()
    embedding = get_embedding(text)
    sanitized_metadata = {}
    if metadata:
        for k, v in metadata.items():
            if isinstance(v, (str, int, float, bool)):
                sanitized_metadata[k] = v
            else:
                sanitized_metadata[k] = str(v)

    collection.upsert(
        ids=[doc_id],
        embeddings=[embedding],
        documents=[text[:1000]],  # Store sample preview
        metadatas=[sanitized_metadata] if sanitized_metadata else None,
    )


def query_similar(text: str, n_results: int = 5) -> list[dict[str, Any]]:
    """Query ChromaDB for documents most similar to input text.

    Args:
        text: Query text.
        n_results: Max results to retrieve.

    Returns:
        List of match dicts with id, distance, document, and metadata.
    """
    collection = get_chroma_collection()
    query_emb = get_embedding(text)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=n_results,
    )

    formatted = []
    if results and "ids" in results and results["ids"]:
        ids = results["ids"][0]
        distances = results.get("distances", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        for i in range(len(ids)):
            formatted.append({
                "id": ids[i],
                "similarity": 1.0 - distances[i] if distances else 0.0,
                "document": documents[i] if documents else "",
                "metadata": metadatas[i] if metadatas else {},
            })

    return formatted


def compute_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between two text snippets (0.0 to 1.0).

    Args:
        text1: First text snippet.
        text2: Second text snippet.

    Returns:
        Cosine similarity score bounded between 0.0 and 1.0.
    """
    if not text1 or not text2:
        return 0.0
    emb1 = np.array(get_embedding(text1))
    emb2 = np.array(get_embedding(text2))

    norm1 = np.linalg.norm(emb1)
    norm2 = np.linalg.norm(emb2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    cosine_sim = float(np.dot(emb1, emb2) / (norm1 * norm2))
    # Bound between 0.0 and 1.0
    return max(0.0, min(1.0, (cosine_sim + 1.0) / 2.0 if cosine_sim < 0 else cosine_sim))
