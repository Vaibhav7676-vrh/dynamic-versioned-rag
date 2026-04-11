from pathlib import Path
from pypdf import PdfReader
from docx import Document
from PIL import Image
import fitz
import zipfile
import io
import pdfplumber
import os

# ----------------------------------
# OCR TOGGLE
# ----------------------------------

USE_OCR = os.getenv("USE_OCR", "false") == "true"

if USE_OCR:
    import pytesseract


# ----------------------------------
# TXT
# ----------------------------------

def extract_text_from_txt(path):
    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    )


# ----------------------------------
# IMAGE OCR
# ----------------------------------

def extract_text_from_image(path):

    if not USE_OCR:
        return "[OCR disabled]"

    image = Image.open(path)
    text = pytesseract.image_to_string(image)

    return text


# ----------------------------------
# PDF TEXT
# ----------------------------------

def extract_text_from_pdf(path):

    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


# ----------------------------------
# PDF TABLE EXTRACTION
# ----------------------------------

def extract_tables_from_pdf(path):

    text = ""

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for table in tables:
                for row in table:
                    row_text = " | ".join(
                        str(cell) if cell else ""
                        for cell in row
                    )
                    text += row_text + "\n"

    return text


# ----------------------------------
# PDF IMAGE OCR
# ----------------------------------

def extract_images_from_pdf(path):

    if not USE_OCR:
        return "[OCR disabled]"

    doc = fitz.open(path)
    text = ""

    for page in doc:
        images = page.get_images()

        for img in images:
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]

            image = Image.open(io.BytesIO(image_bytes))
            text += pytesseract.image_to_string(image)

    return text


# ----------------------------------
# DOCX TEXT
# ----------------------------------

def extract_text_from_docx(path):

    doc = Document(path)
    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text


# ----------------------------------
# DOCX IMAGE OCR
# ----------------------------------

def extract_images_from_docx(path):

    if not USE_OCR:
        return "[OCR disabled]"

    text = ""

    with zipfile.ZipFile(path, "r") as docx:
        for file in docx.namelist():

            if file.startswith("word/media/"):
                image_bytes = docx.read(file)
                image = Image.open(io.BytesIO(image_bytes))

                text += pytesseract.image_to_string(image)

    return text


# ----------------------------------
# MAIN MULTIMODAL EXTRACTION
# ----------------------------------

def extract_content(file_path: Path):

    suffix = file_path.suffix.lower()
    text = ""

    if suffix == ".txt":
        text = extract_text_from_txt(file_path)

    elif suffix == ".pdf":
        text += extract_text_from_pdf(file_path)
        text += extract_tables_from_pdf(file_path)
        text += extract_images_from_pdf(file_path)

    elif suffix == ".docx":
        text += extract_text_from_docx(file_path)
        text += extract_images_from_docx(file_path)

    elif suffix in [".png", ".jpg", ".jpeg"]:
        text += extract_text_from_image(file_path)

    else:
        raise Exception("Unsupported file type")

    return text