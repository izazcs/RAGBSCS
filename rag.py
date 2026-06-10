import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "course_content"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

SYSTEM_PROMPT = """You are a helpful course assistant for computer science curriculum content.
Use only context retrieved from the course content document to answer the user.
If the document does not contain enough information, say that you are not sure."""


def format_documents(docs: list[Document]) -> str:
    entries = []
    for doc in docs:
        source = doc.metadata.get("source", "course_content")
        entries.append(f"[SOURCE: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(entries)


def build_retriever():
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    return vector_store.as_retriever(search_kwargs={"k": 4})


def build_chain():
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY environment variable is required.")

    retriever = build_retriever()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{question}"),
        ]
    )
    llm = ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0,
        max_tokens=None,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
    )
    chain = (
        {"context": retriever | format_documents, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def ask(question: str) -> str:
    chain = build_chain()
    return chain.invoke({"question": question})
