---
title: Course Content RAG
emoji: "📘"
colorFrom: "blue"
colorTo: "green"
sdk: streamlit
sdk_version: "1.34.0"
python_version: "3.11"
app_file: app.py
pinned: false
---

# 📘 Course Content RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built with **Streamlit**, **LangChain**, **ChromaDB**, and **Groq LLM** for interactive Q&A over course content from a PDF document.

## ✨ Features

- 🔐 **Secure Login** - Username/password authentication
- 📚 **Vector Search** - Retrieves relevant course content using ChromaDB
- 💬 **Chat Interface** - Interactive conversation with context-aware responses
- 📝 **Chat History** - Persistent chat history per user (SQLite)
- 🚀 **RAG Architecture** - Combines document retrieval with LLM generation
- ⚡ **Optimized** - Caching for faster responses

## 📂 Project Structure

```
coursecontent-rag-chatbot/
├── app.py                                 # Main Streamlit app
├── requirements.txt                       # Python dependencies (updated for Cloud)
├── .streamlit/
│   ├── config.toml                       # Streamlit configuration
│   └── secrets.toml.example              # Secrets template
├── .gitignore                            # Git ignore rules
├── BCComputerScienceCoursecontent.pdf    # Course content PDF
├── chroma_db/                            # Vector database (generated)
├── chat_history.db                       # Chat history (generated)
├── STREAMLIT_DEPLOYMENT.md               # Cloud deployment guide
└── setup.ps1 / setup.sh                  # Setup scripts
```

## 🚀 Quick Start (Local Development)

### Option 1: Automated Setup (Windows)
```bash
.\setup.ps1
```

### Option 2: Automated Setup (Linux/Mac)
```bash
chmod +x setup.sh
./setup.sh
```

### Option 3: Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .streamlit/secrets.toml
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit .streamlit/secrets.toml with your API keys
# Then run the app
streamlit run app.py
```

## 🔑 Configuration

### Local Development
Create a `.streamlit/secrets.toml` file:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
HUGGINGFACE_TOKEN = "your_huggingface_token_here"  # Optional
```

### Streamlit Cloud
Add secrets in the app settings:
1. Go to your deployed app → App menu → Manage secrets
2. Add:
   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   ```

## 👤 Login Credentials

- **Username:** `admin`
- **Password:** `Khanss`

## 📖 API Keys Required

### 1. **Groq API Key** (Required)
- Get from: https://console.groq.com
- Free tier available for testing

### 2. **HuggingFace Token** (Optional)
- Get from: https://huggingface.co/settings/tokens
- Only needed if using HuggingFace embeddings

## ☁️ Deploy to Streamlit Cloud

**See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for complete deployment guide.**

Quick summary:
1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Click "New app" and select your GitHub repo
4. Add secrets in app settings
5. Deploy!

## 🔧 What's Been Fixed for Cloud

✅ **Fixed git merge conflicts** in `requirements.txt` and `README.md`
✅ **Updated chromadb** from 0.5.23 → 0.4.24
✅ **Updated protobuf** from 3.20.3 → 4.25.1  
✅ **Pinned all dependencies** to stable versions
✅ **Added Streamlit Cloud config** (`.streamlit/config.toml`)
✅ **Added secrets template** (`.streamlit/secrets.toml.example`)
✅ **Updated environment loading** to support Streamlit Cloud secrets
✅ **Excluded sensitive files** from git (`.gitignore`)

## 📊 Performance Metrics

- **First Load:** 2-5 minutes (vector DB initialization)
- **Subsequent Loads:** <1 second (cached)
- **Search Speed:** ~1-2 seconds per query
- **Response Generation:** 2-5 seconds (LLM processing)

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: chromadb` | Run `pip install -r requirements.txt` |
| `protobuf` version conflicts | Already fixed in `requirements.txt` |
| PDF not found | Ensure `BCComputerScienceCoursecontent.pdf` is in the project root |
| API key errors | Check `.streamlit/secrets.toml` or Streamlit Cloud secrets |
| Vector DB not initialized | Click "Refresh knowledge base" in sidebar |

## 📚 Technologies Used

- **Streamlit** - Web framework
- **LangChain** - LLM orchestration
- **Groq API** - Fast LLM inference
- **ChromaDB** - Vector database
- **HuggingFace Embeddings** - Sentence transformers
- **SQLite** - Chat history storage
- **PyPDF** - PDF parsing

## 📝 Files Reference

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit application with chat UI |
| `requirements.txt` | Python dependencies (Cloud-compatible) |
| `config.toml` | Streamlit configuration for Cloud |
| `secrets.toml.example` | Template for API keys |
| `STREAMLIT_DEPLOYMENT.md` | Complete deployment guide |
| `setup.ps1` / `setup.sh` | Automated setup scripts |

## 🤝 Support

- **Streamlit Docs:** https://docs.streamlit.io
- **LangChain Docs:** https://python.langchain.com
- **Groq Console:** https://console.groq.com
- **ChromaDB Docs:** https://docs.trychroma.com

## 📄 License

This project is provided as-is for educational purposes.

---

**Ready to deploy?** See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for step-by-step cloud deployment instructions! 🚀
