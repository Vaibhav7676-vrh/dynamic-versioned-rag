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
        Safe loading (no crash if files missing)
        """

        if not self.versions_file.exists():
            print("No versions.json found → skipping retrieval")
            return

        try:
            versions_data = json.loads(self.versions_file.read_text())
            active_version = versions_data.get("active_version")

            if not active_version:
                print("No active version found")
                return

            if active_version == self.current_version:
                return

            index_path = self.storage_dir / active_version / "index.faiss"
            meta_path = self.storage_dir / active_version / "metadata.pkl"

            if not index_path.exists() or not meta_path.exists():
                print("FAISS files missing → skipping load")
                return

            embedding_dim = 384

            self.store = FaissStore(embedding_dim)
            self.store.load(str(index_path), str(meta_path))

            self.current_version = active_version

        except Exception as e:
            print("Error loading vector store:", e)
            self.store = None

    def retrieve(self, query, k=5):
        """
        Safe retrieval (never crashes)
        """

        try:
            self.load_active_version()

            # No store → return empty
            if self.store is None:
                print("No vector store available")
                return []

            query_embedding = self.embedder.embed_texts([query])

            results = self.store.search(
                query_embedding,
                top_k=k
            )

            return results

        except Exception as e:
            print("Retriever error:", e)
            return []