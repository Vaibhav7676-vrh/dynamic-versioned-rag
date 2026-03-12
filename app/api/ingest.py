from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import json

from pypdf import PdfReader
from docx import Document

from app.ingestion.chunker import chunk_documents
from app.embeddings.embedder import Embedder
from app.vectorstore.faiss_store import FaissStore

router = APIRouter()

STORAGE_DIR = Path("storage")
VERSIONS_FILE = STORAGE_DIR / "versions.json"


def load_versions():

    if not VERSIONS_FILE.exists():
        return {
            "active_version": None,
            "versions": {}
        }

    return json.loads(VERSIONS_FILE.read_text())


def save_versions(data):

    STORAGE_DIR.mkdir(exist_ok=True)

    VERSIONS_FILE.write_text(
        json.dumps(data, indent=2)
    )


# ----------------------------------
# TEXT EXTRACTORS
# ----------------------------------

def extract_text_from_txt(path):

    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


def extract_text_from_pdf(path):

    reader = PdfReader(path)

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def extract_text_from_docx(path):

    doc = Document(path)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


# ----------------------------------
# INGEST ROUTE
# ----------------------------------

@router.post("/ingest-file")
async def ingest_file(file: UploadFile = File(...)):

    versions_data = load_versions()

    # -----------------------------
    # Create new version
    # -----------------------------
    existing_versions = versions_data["versions"].keys()

    new_version_number = len(existing_versions) + 1
    new_version = f"v{new_version_number}"

    version_path = STORAGE_DIR / new_version
    version_path.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # Save uploaded file
    # -----------------------------
    file_path = version_path / file.filename

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # -----------------------------
    # Detect file type
    # -----------------------------
    suffix = file_path.suffix.lower()

    if suffix == ".txt":

        text = extract_text_from_txt(file_path)

    elif suffix == ".pdf":

        text = extract_text_from_pdf(file_path)

    elif suffix == ".docx":

        text = extract_text_from_docx(file_path)

    else:

        return {
            "error": "Unsupported file type. Use txt, pdf, or docx."
        }

    # -----------------------------
    # Convert to documents
    # -----------------------------
    docs = [
        {
            "text": text,
            "metadata": {
                "source": file.filename
            }
        }
    ]

    # -----------------------------
    # Chunk documents
    # -----------------------------
    chunks = chunk_documents(docs)

    embedder = Embedder()

    texts = [c["text"] for c in chunks]

    embeddings = embedder.embed_texts(texts)

    embedding_dim = embeddings.shape[1]

    store = FaissStore(embedding_dim)

    metadatas = [c["metadata"] for c in chunks]

    store.add(embeddings, metadatas)

    # -----------------------------
    # Save FAISS
    # -----------------------------
    store.save(
        str(version_path / "index.faiss"),
        str(version_path / "metadata.pkl")
    )

    # -----------------------------
    # Update versions
    # -----------------------------
    versions_data["versions"][new_version] = [
        file.filename
    ]

    versions_data["active_version"] = new_version

    save_versions(versions_data)

    return {
        "message": "File ingested successfully",
        "version": new_version
    }