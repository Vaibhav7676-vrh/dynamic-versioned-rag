import faiss
import numpy as np
import pickle
from typing import List, Dict


class FaissStore:
    def __init__(self, embedding_dim: int):
        self.embedding_dim = embedding_dim
        self.index = faiss.IndexFlatIP(embedding_dim)  
        self.metadata: List[Dict] = []

    def add(self, embeddings: np.ndarray, metadatas: List[Dict]):
        """
        Add vectors and metadata to the index
        """
        self.index.add(embeddings)
        self.metadata.extend(metadatas)

    def search(self, query_vector: np.ndarray, top_k: int = 5):
        """
        Search similar vectors
        """
        scores, indices = self.index.search(query_vector, top_k)
        results = []

        for idx, score in zip(indices[0], scores[0]):
            if idx == -1:
                continue
            results.append({
                "score": float(score),
                "metadata": self.metadata[idx]
            })
        return results

    def save(self, index_path: str, meta_path: str):
        faiss.write_index(self.index, index_path)
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self, index_path: str, meta_path: str):
        self.index = faiss.read_index(index_path)
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
