import os
import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
import logging
import traceback
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent
CHROMA_DIR = BASE_DIR / "chroma_db"
SQLITE_PATH = BASE_DIR / "chat_history.db"
PDF_PATH = BASE_DIR / "BCComputerScienceCoursecontent.pdf"
COLLECTION_NAME = "course_content"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
CHUNK_SEPARATORS = ["\n\n", "\n", ".", " "]
USERNAME = "admin"
PASSWORD = "Khanss"

OUT_OF_SCOPE_REPLY = "I Dont know about this topic!"

SYSTEM_PROMPT = f"""You are a helpful course assistant for computer science curriculum content.
Answer the user's questions using ONLY the context retrieved from the course content document.
Do NOT use any external knowledge or make any assumptions beyond the document's content.
If the document does not contain enough information to answer the question, reply exactly: {OUT_OF_SCOPE_REPLY}
If the question is unrelated to the document, reply exactly: {OUT_OF_SCOPE_REPLY}"""

st.set_page_config(page_title="Course Content RAG", page_icon="📘", layout="wide")

# setup logging to file for errors only
LOG_PATH = BASE_DIR / "app_error.log"
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)


def load_environment():
    """Load environment variables from .env file or Streamlit secrets"""
    # First, try to load from local .env file
    local_env = BASE_DIR / ".env"
    if local_env.exists():
        load_dotenv(dotenv_path=local_env, override=True)
    
    # For Streamlit Cloud, secrets are available via st.secrets
    # Try to get GROQ_API_KEY from secrets first, fall back to env
    try:
        if "GROQ_API_KEY" in st.secrets:
            key = st.secrets["GROQ_API_KEY"]
            if key:
                clean = key.strip().strip('"').strip("'")
                os.environ["GROQ_API_KEY"] = clean
    except Exception:
        # st.secrets might not be available in all contexts
        pass
    
    # Ensure at least try the environment variable
    key = os.getenv("GROQ_API_KEY")
    if key:
        clean = key.strip().strip('"').strip("'")
        os.environ["GROQ_API_KEY"] = clean


def init_db():
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_message(username: str, role: str, content: str):
    # ensure content is a string before saving
    content = str(content)
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (username, role, content, created_at) VALUES (?, ?, ?, ?)",
        (username, role, content, datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def load_messages(username: str):
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content, created_at FROM messages WHERE username = ? ORDER BY id",
        (username,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def clear_history(username: str):
    conn = sqlite3.connect(SQLITE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE username = ?", (username,))
    conn.commit()
    conn.close()


def ingest_course_content():
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


def ensure_vector_store():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    if not any(CHROMA_DIR.iterdir()):
        ingest_course_content()


@st.cache_resource
def get_retriever():
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    ).as_retriever(search_kwargs={"k": 6})


def get_vector_count() -> int:
    if not CHROMA_DIR.exists():
        return 0
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    db = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )
    try:
        return len(db._collection.get()["ids"])
    except Exception:
        return 0


@st.cache_resource
def get_llm(groq_key: str):
    # Ensure the groq key is present and included in the cache key
    if not groq_key:
        raise RuntimeError("GROQ_API_KEY is missing for LLM creation")
    # sanitize the key (strip quotes/spaces) and set into env for client libs
    clean = groq_key.strip().strip('"').strip("'")
    os.environ["GROQ_API_KEY"] = clean
    return ChatGroq(
        model="qwen/qwen3-32b",
        temperature=0,
        max_tokens=None,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
    )


def format_documents(docs: list[Document]) -> str:
    entries = []
    for doc in docs:
        source = doc.metadata.get("source", "course_content")
        entries.append(f"[SOURCE: {source}]\n{doc.page_content}")
    return "\n\n---\n\n".join(entries)


def normalize_chain_response(result):
    # Convert many possible chain return types into a plain string for Streamlit
    def _is_out_of_scope_text(s: str) -> bool:
        low = s.lower()
        patterns = [
            "don't know",
            "do not know",
            "i don't know",
            "i do not know",
            "insufficient",
            "not enough",
            "no information",
            "not in the document",
            "cannot answer",
            "can't answer",
            "out of scope",
            "no relevant",
        ]
        return any(p in low for p in patterns)

    try:
        res_str = ""
        # dict-like responses
        if isinstance(result, dict):
            for key in ("output", "response", "result", "answer", "text"):
                if key in result:
                    res_str = str(result[key])
                    break

            if not res_str and "messages" in result and isinstance(result["messages"], (list, tuple)):
                msgs = result["messages"]
                if msgs:
                    last = msgs[-1]
                    if isinstance(last, dict) and "content" in last:
                        res_str = str(last["content"])
                    elif hasattr(last, "content"):
                        res_str = str(last.content)
                if not res_str:
                    res_str = str(result["messages"])

            if not res_str:
                res_str = str(result)

        # list-like responses: join textual elements
        elif isinstance(result, (list, tuple)):
            parts = []
            for item in result:
                if isinstance(item, dict):
                    for key in ("content", "text", "answer"):
                        if key in item:
                            parts.append(str(item[key]))
                            break
                    else:
                        parts.append(str(item))
                elif hasattr(item, "page_content"):
                    parts.append(str(item.page_content))
                elif hasattr(item, "content"):
                    parts.append(str(item.content))
                else:
                    parts.append(str(item))
            res_str = "\n\n".join(parts)

        # objects with common attributes
        elif hasattr(result, "content"):
            res_str = str(result.content)
        elif hasattr(result, "page_content"):
            res_str = str(result.page_content)
        else:
            res_str = str(result)
    except Exception:
        res_str = str(result)

    # enforce strict out-of-scope reply
    if _is_out_of_scope_text(res_str):
        return OUT_OF_SCOPE_REPLY

    return res_str


def answer_question(question: str) -> str:
    load_environment()
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError(
            "GROQ_API_KEY is missing. Set it in your environment or in a .env file."
        )

    ensure_vector_store()
    retriever = get_retriever()

    # Get relevant docs as plain text context (ensure we pass a string to the embedding layer)
    try:
        # Try common retriever methods in order of likelihood
        docs = None
        for method in (
            "get_relevant_documents",
            "get_relevant_documents_async",
            "get_documents",
            "get_relevant_documents_from_query",
            "get_relevant_documents_sync",
        ):
            fn = getattr(retriever, method, None)
            if callable(fn):
                docs = fn(question)
                break

        # Fallbacks: direct similarity_search on retriever or underlying vectorstore
        if docs is None:
            if getattr(retriever, "similarity_search", None):
                docs = retriever.similarity_search(question)
            elif getattr(retriever, "vectorstore", None) and getattr(retriever.vectorstore, "similarity_search", None):
                docs = retriever.vectorstore.similarity_search(question)

        if docs is None:
            raise RuntimeError("Retriever does not expose a known document-fetching API")
    except Exception:
        logging.exception("Retriever failed")
        raise

    context_text = format_documents(docs)

    # include context in the system prompt so the LLM only answers from it
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT + "\n\nCONTEXT:\n{context}"),
            ("human", "{question}"),
        ]
    )

    chain = prompt | get_llm(os.getenv("GROQ_API_KEY")) | StrOutputParser()
    try:
        result = chain.invoke({"question": question, "context": context_text})
        return normalize_chain_response(result)
    except Exception:
        logging.exception("LLM chain invocation failed")
        raise


def render_login():
    st.title("🔐 Course Content RAG Login")
    st.write("Enter the fixed user credentials to access the course chat assistant.")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Sign in")

    if login:
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("Invalid username or password. Use admin / Khanss.")


def render_sidebar(username: str):
    st.sidebar.title("Course Content Assistant")
    st.sidebar.markdown("**Logged in as:** ``%s``" % username)
    st.sidebar.info("Fixed login: admin / Khanss")

    if st.sidebar.checkbox("Show index stats"):
        st.sidebar.markdown(f"- **Vector store:** `{CHROMA_DIR}`")
        st.sidebar.markdown(f"- **Stored vectors:** {get_vector_count()}")
        st.sidebar.markdown(f"- **Chunk size:** {CHUNK_SIZE}")
        st.sidebar.markdown(f"- **Chunk overlap:** {CHUNK_OVERLAP}")
        st.sidebar.markdown(f"- **Search k:** 4")
        st.sidebar.markdown(f"- **Chunks created from PDF:** 338 (approx)")
        st.sidebar.markdown(f"- **Stored vector count may differ if ingestion was partial or repeated")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None

    if st.sidebar.button("Refresh knowledge base"):
        ingest_course_content()
        st.sidebar.success("Knowledge base refreshed.")

    if st.sidebar.button("Clear chat history"):
        clear_history(username)
        st.sidebar.success("Chat history cleared.")

    history = load_messages(username)
    st.sidebar.markdown("---")
    st.sidebar.subheader("Chat history")
    if history:
        for role, content, created_at in history[-20:]:
            label = "You" if role == "user" else "Assistant"
            st.sidebar.markdown(f"**{label}**: {content}")
    else:
        st.sidebar.write("No history yet.")


def render_chat_interface():
    st.title("📘 Course Content Chat")
    st.caption("Ask questions about the computer science course document and get answers with retrieval-augmented generation.")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(str(message.get("content", "")))

    prompt = st.chat_input("Ask about the course content...")
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": str(prompt)})
        save_message(st.session_state.username, "user", str(prompt))
        with st.chat_message("assistant"):
            with st.spinner("Searching the course content..."):
                try:
                    response = answer_question(prompt)
                except Exception as exc:
                    # capture and show full traceback in UI and log file
                    tb = traceback.format_exc()
                    logging.exception("Error while answering question")
                    response = f"Error: {exc}"
                    # display traceback in an expander for debugging
                    with st.expander("Error details"):
                        st.code(tb)
            st.markdown(str(response))
        st.session_state.chat_messages.append({"role": "assistant", "content": str(response)})
        save_message(st.session_state.username, "assistant", str(response))


def main():
    load_environment()
    init_db()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    if not st.session_state.logged_in:
        render_login()
        return

    render_sidebar(st.session_state.username)
    render_chat_interface()


if __name__ == "__main__":
    main()
