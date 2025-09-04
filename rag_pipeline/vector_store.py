import faiss
import os
import pickle

class FaissStore:
    def __init__(self, index, texts):
        self.index = index
        self.texts = texts

def save_faiss_index(texts, embeddings, path):
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    store = FaissStore(index=index, texts=texts)
    with open(path, "wb") as f:
        pickle.dump(store, f)
    return store

def load_faiss_index(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None