# rag_pipeline/loader.py
import os
from typing import List
from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_texts_from_folder(folder: str) -> List[str]:
    texts = []
    if not os.path.isdir(folder):
        return texts
    for root, _, files in os.walk(folder):
        for fn in files:
            if fn.lower().endswith((".txt", ".md", ".markdown")):
                path = os.path.join(root, fn)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        texts.append(f.read())
                except Exception:
                    # skip unreadable files
                    pass
    return texts

def chunk_texts(texts: List[str], chunk_size: int = 1000, chunk_overlap: int = 200):
    docs = [Document(page_content=t) for t in texts if t.strip()]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)

def load_documents(folder: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    texts = load_texts_from_folder(folder)
    return chunk_texts(texts, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
