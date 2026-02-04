from pathlib import Path
from typing import List, Dict


def load_text_documents(folder_path: str) -> List[Dict]:
    documents = []
    folder = Path(folder_path)

    for file_path in folder.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append({
            "text": text,
            "metadata": {
                "source": file_path.name
            }
        })

    return documents
