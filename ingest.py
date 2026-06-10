import os
import urllib.request
import urllib.error
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "BCComputerScienceCoursecontent.pdf"
PDF_URL = "https://uom.edu.pk/storage/csit/downloads//1756185259/1756185259-[FILE]-Annexure-A--CS-Acadamic-Council.pdf"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "course_content"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def download_pdf():
    if PDF_PATH.exists():
        return
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Referer": PDF_URL,
    }
    request = urllib.request.Request(PDF_URL, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            with open(PDF_PATH, "wb") as out_file:
                out_file.write(response.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            raise RuntimeError(
                f"PDF download blocked with HTTP 403 from {PDF_URL}. "
                "That host may block automated downloads. "
                "Upload the PDF manually to the Space or use an alternate public URL."
            ) from exc
        raise RuntimeError(f"Failed to download PDF from {PDF_URL}: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Failed to download PDF from {PDF_URL}: {exc}") from exc


def ingest_course_content():
    if not PDF_PATH.exists():
        download_pdf()
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF file not found: {PDF_PATH}")

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    loader = PyPDFLoader(str(PDF_PATH))
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_documents(pages)
    for idx, chunk in enumerate(chunks):
        chunk.metadata["source"] = PDF_PATH.name
        chunk.metadata["chunk_index"] = idx

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )


if __name__ == "__main__":
    print("Ingesting course content into Chroma...")
    ingest_course_content()
    print("Ingestion complete.")
