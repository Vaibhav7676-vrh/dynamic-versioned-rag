from app.ingestion.loader import load_text_documents
from app.ingestion.chunker import chunk_documents
from app.embeddings.embedder import Embedder

if __name__ == "__main__":
    docs = load_text_documents("data/sample_docs")
    chunks = chunk_documents(docs)

    texts = [c["text"] for c in chunks]

    embedder = Embedder()
    vectors = embedder.embed_texts(texts)

    print("Chunks:", len(texts))
    print("Embedding shape:", vectors.shape)
