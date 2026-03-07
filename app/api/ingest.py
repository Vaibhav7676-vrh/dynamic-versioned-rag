from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import json

from app.embeddings.embedder import Embedder
from app.vectorstore.faiss_store import FaissStore
from app.ingestion.chunker import chunk_documents
router = APIRouter()

STORAGE_DIR = Path("storage")
VERSIONS_FILE = STORAGE_DIR / "versions.json"


def load_versions():
    if not VERSIONS_FILE.exists():
        return {"active_version": None, "versions": {}}
    return json.loads(VERSIONS_FILE.read_text())


def save_versions(data):
    STORAGE_DIR.mkdir(exist_ok=True)
    VERSIONS_FILE.write_text(json.dumps(data, indent=2))


# ----------------------------
# INGEST FILE
# ----------------------------
@router.post("/ingest-file")
async def ingest_file(file: UploadFile = File(...)):

    versions_data = load_versions()

    # Determine new version
    existing_versions = versions_data["versions"].keys()
    new_version_number = len(existing_versions) + 1
    new_version = f"v{new_version_number}"

    version_path = STORAGE_DIR / new_version
    version_path.mkdir(parents=True, exist_ok=True)

    # Save uploaded file
    file_path = version_path / file.filename
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Read file text
    text = file_path.read_text(encoding="utf-8")

    docs = [{"text": text, "metadata": {"source": file.filename}}]
    chunks = chunk_documents(docs)

    embedder = Embedder()
    texts = [c["text"] for c in chunks]
    embeddings = embedder.embed_texts(texts)

    embedding_dim = embeddings.shape[1]
    store = FaissStore(embedding_dim)

    metadatas = [c["metadata"] for c in chunks]
    store.add(embeddings, metadatas)

    store.save(
        str(version_path / "index.faiss"),
        str(version_path / "metadata.pkl")
    )

    # Update versions.json
    versions_data["versions"][new_version] = [file.filename]
    versions_data["active_version"] = new_version

    save_versions(versions_data)

    return {
        "message": "File ingested",
        "version": new_version
    }


# ----------------------------
# GET VERSIONS
# ----------------------------
@router.get("/versions")
def get_versions():
    return load_versions()