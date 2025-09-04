# rag_pipeline/__init__.py
import os
from typing import Optional
from vertexai.preview.generative_models import GenerativeModel

from .loader import load_texts_from_folder, chunk_texts
from .embedder import embed_documents, load_faiss_index
from .retriever import retrieve_context


def _index_exists(path: str) -> bool:
    # FAISS saves multiple files; presence of 'index.faiss' is enough
    if not os.path.isdir(path):
        return False
    for fn in os.listdir(path):
        if fn.endswith(".faiss"):
            return True
    return False


def ask_with_rag(
    query: str,
    model: str = "gemini-1.5-pro",
    kb_path: str = "data/knowledge_base",
    k: int = 3,
    cfg: Optional[dict] = None,
):
    """
    - Loads/Chunks KB
    - Builds or loads FAISS (embeddings: Vertex→HF fallback)
    - Retrieves top-k context
    - Calls LLM (Vertex GenerativeModel) to answer
      (If LLM fails on Streamlit Cloud due to GCP auth, returns context-only answer instead of crashing.)
    """
    # 1) Load and chunk
    texts = load_texts_from_folder(kb_path)
    if not texts:
        return "⚠️ No knowledge base documents found. Please upload `.txt` or `.md` files."

    chunks = chunk_texts(texts)
    if not chunks:
        return "⚠️ Knowledge base documents are empty or could not be split."

    # 2) Build or load FAISS
    index_path = (cfg or {}).get("vector_store", {}).get("path", "faiss_index")
    if _index_exists(index_path):
        try:
            db = load_faiss_index(index_path, cfg=cfg)
        except Exception:
            # Corrupted or incompatible index; rebuild
            db = embed_documents(chunks, save_path=index_path, cfg=cfg)
    else:
        db = embed_documents(chunks, save_path=index_path, cfg=cfg)

    # 3) Retrieve context
    context = retrieve_context(query, db, top_k=k)
    full_prompt = f"{context}\n\nUser Query: {query}\nAnswer:"

    # 4) Generate answer via Vertex (soft-fail if unavailable)
    try:
        gemini = GenerativeModel(model)
        response = gemini.generate_content(full_prompt)
        return (response.text or "").strip() or context
    except Exception as e:
        # On Streamlit Cloud (no GCP project/metadata), we still return something useful
        return f"(Model unavailable; showing context-only answer)\n\n{context}"
