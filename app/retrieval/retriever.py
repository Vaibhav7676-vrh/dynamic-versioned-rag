import os
import json
import numpy as np

from app.vectorstore.faiss_store import FaissStore
from app.embeddings.embedder import Embedder


class Retriever:

    def __init__(self, top_k: int = 5):
        self.top_k = top_k

        versions_file = os.path.join("storage", "versions.json")

        if not os.path.exists(versions_file):
            raise ValueError("No versions found. Please ingest documents first.")

        with open(versions_file, "r") as f:
            data = json.load(f)

        # Support both dict and list formats
        if isinstance(data, dict):
            versions = data.get("versions", [])
        else:
            versions = data

        if not versions:
            raise ValueError("No versions available.")

        latest_version = versions[-1]

        index_path = os.path.join("storage", latest_version, "index.faiss")
        meta_path = os.path.join("storage", latest_version, "metadata.pkl")

        if not os.path.exists(index_path):
            raise ValueError(f"Index file not found for version {latest_version}")

        # MiniLM embedding dimension = 384
        self.store = FaissStore(384)
        self.store.load(index_path, meta_path)

        self.embedder = Embedder()

    def search(self, query: str, k: int = None):
        if k is None:
            k = self.top_k

        # Embed query
        query_embedding = self.embedder.embed_texts([query])

        if len(query_embedding.shape) < 2:
            raise ValueError("Query embedding failed.")

        # Search in FAISS
        results = self.store.search(query_embedding, top_k=k)

        return results