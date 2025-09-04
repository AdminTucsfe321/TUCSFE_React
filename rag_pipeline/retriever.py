# rag_pipeline/retriever.py
from typing import Any

def retrieve_context(query: str, faiss_db: Any, top_k: int = 3) -> str:
    """
    Uses FAISS VectorStore's similarity_search to get top_k docs and
    returns a concatenated context string.
    """
    hits = faiss_db.similarity_search(query, k=top_k)
    return "\n\n".join(d.page_content for d in hits if getattr(d, "page_content", None))
