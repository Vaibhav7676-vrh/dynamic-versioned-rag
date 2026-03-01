from fastapi import APIRouter, UploadFile, File
import os
import shutil
import json

from app.ingestion.loader import load_text_documents
from app.ingestion.chunker import chunk_documents
from app.embeddings.embedder import Embedder
from app.vectorstore.faiss_store import FaissStore

router = APIRouter()

UPLOAD_DIR = "data/uploads"
STORAGE_DIR = "storage"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR, exist_ok=True)


@router.post("/ingest-file")
async def ingest_file(file: UploadFile = File(...)):

    # 1️⃣ Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2️⃣ Load documents from uploads folder
    docs = load_text_documents(UPLOAD_DIR)

    if not docs:
        return {"error": "No documents found in uploads folder"}

    # 3️⃣ Chunk
    chunks = chunk_documents(docs)

    if not chunks:
        return {"error": "Chunking produced no results"}

    texts = [chunk["text"] for chunk in chunks]

    # 4️⃣ Embed
    embedder = Embedder()
    embeddings = embedder.embed_texts(texts)

    if len(embeddings.shape) < 2:
        return {"error": "Embedding generation failed"}

    embedding_dim = embeddings.shape[1]

    # 5️⃣ Create FAISS store
    store = FaissStore(embedding_dim)
    store.add(embeddings, chunks)

    # 6️⃣ Handle versions.json safely
    versions_file = os.path.join(STORAGE_DIR, "versions.json")

    if os.path.exists(versions_file):
        with open(versions_file, "r") as f:
            data = json.load(f)

        # If it's a dict like {"versions": [...]}
        if isinstance(data, dict):
            versions = data.get("versions", [])
        else:
            versions = data
    else:
        versions = []

    # 7️⃣ Create new version
    new_version_number = len(versions) + 1
    new_version = f"v{new_version_number}"

    version_dir = os.path.join(STORAGE_DIR, new_version)
    os.makedirs(version_dir, exist_ok=True)

    index_path = os.path.join(version_dir, "index.faiss")
    meta_path = os.path.join(version_dir, "metadata.pkl")

    store.save(index_path, meta_path)

    # 8️⃣ Update versions list
    versions.append(new_version)

    # Save back in same format (dict style)
    with open(versions_file, "w") as f:
        json.dump({"versions": versions}, f, indent=4)

    return {"message": f"{file.filename} ingested into {new_version}"}