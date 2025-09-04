import os
import numpy as np
import vertexai
from vertexai.language_models import TextEmbeddingModel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class VertexAIEmbeddings:
    def __init__(self, model, project, location):
        import vertexai
        from vertexai.language_models import TextEmbeddingModel
        vertexai.init(project=project, location=location)
        self.model = TextEmbeddingModel.from_pretrained(model)

    def embed_documents(self, docs):
        texts = [d.page_content if hasattr(d, 'page_content') else d for d in docs]
        return [self.model.get_embeddings([t])[0].values for t in texts]

    def embed_query(self, text):
        return self.model.get_embeddings([text]).values


class VertexOrHFEmbeddings:
    def __init__(self, cfg):
        self.cfg = cfg
        try:
            print("[Embeddings] Using Vertex AI ✅")
            self.vertex = VertexAIEmbeddings(
                model="textembedding-gecko",
                project=cfg["project_id"],
                location=cfg.get("location", "us-central1"),
            )
            self.hf = None
            self.use_vertex = True
        except Exception as e:
            print(f"[Warning] Vertex embedding init failed: {e}")
            self.vertex = None
            self.hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.use_vertex = False

    def embed_documents(self, texts):
        try:
            if self.use_vertex and self.vertex:
                return self.vertex.embed_documents(texts)
        except Exception as e:
            print(f"[Warning] Vertex embedding failed, falling back to HF: {e}")
            self.use_vertex = False
            self.hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        return self.hf.embed_documents(texts)

    def embed_query(self, text):
        try:
            if self.use_vertex and self.vertex:
                return self.vertex.embed_query(text)
        except Exception as e:
            print(f"[Warning] Vertex query embedding failed, falling back to HF: {e}")
            self.use_vertex = False
            self.hf = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        return self.hf.embed_query(text)

    # 👇 this makes FAISS happy
    def __call__(self, text):
        return self.embed_query(text)


def embed_documents(docs, save_path="faiss_index",cfg=None):
    embeddings = VertexOrHFEmbeddings(cfg)
    db = FAISS.from_documents(docs, embedding=embeddings)
    db.save_local(save_path)
    return db


def load_faiss_index(save_path="faiss_index",cfg=None):
    embeddings = VertexOrHFEmbeddings(cfg)
    return FAISS.load_local(save_path, embeddings, allow_dangerous_deserialization=True)
