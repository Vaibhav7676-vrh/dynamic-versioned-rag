import json
from pathlib import Path

from app.embeddings.embedder import Embedder
from app.vectorstore.faiss_store import FaissStore


class Retriever:

    def __init__(self):
        self.embedder = Embedder()

        self.storage_dir = Path("storage")
        self.versions_file = self.storage_dir / "versions.json"

        self.store = None
        self.current_version = None

    def load_active_version(self):
        """
        Loads the active FAISS index based on versions.json
        """

        if not self.versions_file.exists():
            raise Exception("versions.json not found")

        versions_data = json.loads(self.versions_file.read_text())

        active_version = versions_data.get("active_version")

        if not active_version:
            raise Exception("No active version found")

        if active_version == self.current_version:
            return

        index_path = self.storage_dir / active_version / "index.faiss"
        meta_path = self.storage_dir / active_version / "metadata.pkl"

        embedding_dim = 384  # dimension for MiniLM

        self.store = FaissStore(embedding_dim)
        self.store.load(str(index_path), str(meta_path))

        self.current_version = active_version

    def retrieve(self, query, k=5):
        """
        Retrieves top-k relevant chunks for the query
        """

        # Load latest version automatically
        self.load_active_version()

        # Convert query to embedding
        query_embedding = self.embedder.embed_texts([query])

        # Search FAISS
        results = self.store.search(
            query_embedding,
            top_k=k
        )

        return results