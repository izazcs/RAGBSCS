<<<<<<< HEAD
---
title: Course Content RAG
emoji: "📘"
colorFrom: "blue"
colorTo: "green"
sdk: streamlit
sdk_version: "1.24.0"
python_version: "3.11"
app_file: app.py
pinned: false
---

# Course Content RAG

This folder contains a Streamlit-based RAG application for the course content PDF `BCComputerScienceCoursecontent.pdf`.

## Files

- `app.py` - Streamlit chat interface with login, chat history, and RAG query processing.
- `ingest.py` - Ingests the PDF into a Chroma vector store.
- `rag.py` - Builds the retrieval chain using Chroma embeddings and Groq LLM.
- `db.py` - SQLite helpers for storing user chat history.
- `requirements.txt` - Python dependencies for Hugging Face Spaces.

## Setup

1. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

2. Set your `GROQ_API_KEY` in the local `.env` file.
   - The app now loads only `courseContentRAG/coursecontent-rag-chatbot/.env`.
   - On Hugging Face Spaces, add `GROQ_API_KEY` as a secret.

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Login Credentials

- Username: `student`
- Password: `course2026`

## Notes for Hugging Face Spaces

- Set `GROQ_API_KEY` in the Space secrets.
- The app automatically creates `chroma_db` and `chat_history.db` in the `courseContentRAG` directory.
- If the knowledge base is missing, use the sidebar "Refresh knowledge base" button to ingest the PDF.
=======
# RAGBSCS
A RAG project of BS CS UOM Course contents.
>>>>>>> 25fdd73ba2f754443b8b6fdba3cf2a4527cc8fbe
