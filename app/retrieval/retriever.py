import json
from pathlib import Path
from typing import List, Dict

from app.embeddings.embedder import Embedder
from app.vectorstore.faiss_store import FaissStore


STORAGE_DIR = Path("storage")
VERSIONS_FILE = STORAGE_DIR / "versions.json"


class Retriever:
    def __init__(self):
        self.embedder = Embedder()

        # Load versions metadata
        if not VERSIONS_FILE.exists():
            raise Exception("versions.json not found")

        versions_data = json.loads(VERSIONS_FILE.read_text())

        active_version = versions_data.get("active_version")

        if not active_version:
            raise Exception("No active version available")

        index_path = STORAGE_DIR / active_version / "index.faiss"
        meta_path = STORAGE_DIR / active_version / "metadata.pkl"

        if not index_path.exists():
            raise Exception(f"FAISS index not found for version {active_version}")

        # Load FAISS index
        self.store = FaissStore(384)  # MiniLM embedding size
        self.store.load(str(index_path), str(meta_path))

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve top-k most similar chunks
        """

        # Create query embedding
        query_embedding = self.embedder.embed_texts([query])

        # IMPORTANT: positional argument used to avoid keyword errors
        results = self.store.search(query_embedding, top_k)

        return results