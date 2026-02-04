from app.ingestion.loader import load_text_documents
from app.ingestion.chunker import chunk_documents
from app.embeddings.embedder import Embedder
from app.vectorstore.faiss_store import FaissStore
import numpy as np


if __name__ == "__main__":
    docs = load_text_documents("data/sample_docs")
    chunks = chunk_documents(docs)

    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    embedder = Embedder()
    vectors = embedder.embed_texts(texts)

    store = FaissStore(embedding_dim=vectors.shape[1])
    store.add(vectors, metadatas)

    query = "What is RAG?"
    query_vec = embedder.embed_texts([query])

    results = store.search(query_vec, top_k=3)

    print("Search results:")
    for r in results:
        print(r)
