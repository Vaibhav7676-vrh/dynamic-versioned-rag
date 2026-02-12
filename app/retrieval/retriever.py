
from app.embeddings.embedder import Embedder
from app.vectorstore.faiss_store import FaissStore
from app.ingestion.version_manager import VersionManager
from app.retrieval.reranker import Reranker



class Retriever:

    def __init__(self):

        # Create embedder
        self.embedder = Embedder()

        # Get latest version
        vm = VersionManager()
        version = vm.get_latest_version()

        index_path = f"storage/{version}/index.faiss"
        meta_path = f"storage/{version}/metadata.pkl"

        # Create FAISS store
        self.store = FaissStore(embedding_dim=384)
        
        self.reranker = Reranker()


        # Load index
        self.store.load(index_path, meta_path)

    def search(self, query: str, k: int = 3, threshold: float = 0.40):

        query_embedding = self.embedder.embed_texts([query])

        raw_results = self.store.search(query_embedding, k)

        filtered_results = []

        for r in raw_results:
            if r["score"] >= threshold:
                filtered_results.append(r)

        reranked = self.reranker.rerank(query, filtered_results)
        return reranked

