from app.ingestion.loader import load_text_documents
from app.ingestion.chunker import chunk_documents
from app.ingestion.version_manager import VersionManager
from app.embeddings.embedder import Embedder
from app.vectorstore.faiss_store import FaissStore


if __name__ == "__main__":
    docs = load_text_documents("data/sample_docs")
    chunks = chunk_documents(docs)

    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    embedder = Embedder()
    vectors = embedder.embed_texts(texts)

    vm = VersionManager()
    version = vm.create_new_version()

    store = FaissStore(embedding_dim=vectors.shape[1])
    store.add(vectors, metadatas)

    index_path = f"storage/{version}/index.faiss"
    meta_path = f"storage/{version}/metadata.pkl"

    store.save(index_path, meta_path)

    print(f"Created version: {version}")
