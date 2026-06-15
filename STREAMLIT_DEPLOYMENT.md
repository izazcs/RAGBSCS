# 🚀 Streamlit Cloud Deployment Guide

## Overview
This guide will help you deploy the Course Content RAG Chatbot to Streamlit Cloud. We've fixed all dependency issues and made the app cloud-ready.

---

## Step 1: Prerequisites

Before deploying, ensure you have:
- ✅ A GitHub account
- ✅ A Groq API key (from https://console.groq.com)
- ✅ A HuggingFace token (optional, for embeddings)

---

## Step 2: Prepare Your Local Repository

### 2.1 Update Dependencies
The `requirements.txt` has been updated with compatible versions for Streamlit Cloud:
- ✅ chromadb==0.4.24 (fixed from 0.5.23)
- ✅ protobuf==4.25.1 (fixed from 3.20.3)
- ✅ All other dependencies pinned to stable versions

### 2.2 Verify Your Setup Locally
Test the app locally before deploying:

```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Create .streamlit/secrets.toml with your API keys
# Copy .streamlit/secrets.toml.example to .streamlit/secrets.toml
# Fill in your actual API keys

# Run the app
streamlit run app.py
```

---

## Step 3: Create a GitHub Repository

### 3.1 Initialize Git (if not already done)
```bash
cd coursecontent-rag-chatbot
git init
```

### 3.2 Create a New Repository on GitHub
1. Go to https://github.com/new
2. Create a repository named: `coursecontent-rag-chatbot` (or your preferred name)
3. Don't add README, .gitignore, or license (they already exist)

### 3.3 Push Your Code to GitHub
```bash
git add .
git commit -m "Initial commit: RAG chatbot ready for Streamlit Cloud"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/coursecontent-rag-chatbot.git
git push -u origin main
```

---

## Step 4: Deploy to Streamlit Cloud

### 4.1 Connect Streamlit Cloud to GitHub
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your GitHub repository
4. Choose the branch: `main`
5. Set the main file path: `app.py`
6. Click "Deploy"

### 4.2 Add Secrets in Streamlit Cloud
Once deployed, configure your API keys:

1. Click on your deployed app (three dots menu → Edit secrets)
2. Add the following secrets:

```toml
GROQ_API_KEY = "your_groq_api_key"
HUGGINGFACE_TOKEN = "your_huggingface_token"  # Optional
```

**Important:** Never commit your `.streamlit/secrets.toml` file to GitHub. It's already in `.gitignore`.

---

## Step 5: Handle Vector Database Initialization

### Issue
The Chroma vector database is built from the PDF on first load. This could be slow on Streamlit Cloud's first run.

### Solution
The app automatically:
1. Loads the PDF (`BCComputerScienceCoursecontent.pdf`)
2. Creates embeddings on first run
3. Caches the vector store for subsequent requests

**First Load:** May take 2-5 minutes (normal)
**Subsequent Loads:** <1 second (cached)

---

## Step 6: Verify Your Deployment

1. Open your Streamlit Cloud app URL
2. Wait for first initialization (loading vector database)
3. Test the chat functionality
4. Check that your secrets are correctly loaded

---

## Troubleshooting

### Issue: ModuleNotFoundError for chromadb
**Solution:** Make sure `requirements.txt` has pinned versions (done ✅)

### Issue: protobuf version conflicts
**Solution:** Updated to `protobuf==4.25.1` (done ✅)

### Issue: HuggingFace model downloads
**Solution:** Models cache automatically. First run takes longer.

### Issue: App crashes after deployment
1. Check Streamlit Cloud logs (App menu → Logs)
2. Verify secrets are added correctly
3. Check that API keys are valid

### Issue: PDF not found
**Solution:** Ensure `BCComputerScienceCoursecontent.pdf` is in the same directory as `app.py` and committed to GitHub

---

## Performance Tips

1. **Caching:** The `@st.cache_resource` decorator caches the retriever, reducing load time
2. **Vector Store:** Builds once and reuses across sessions
3. **Chat History:** Stored in SQLite (persistent across redeployments)

---

## File Structure for Deployment

```
coursecontent-rag-chatbot/
├── .streamlit/
│   ├── config.toml          # ← Streamlit configuration
│   └── secrets.toml.example # ← Template (not pushed to GitHub)
├── app.py                    # ← Main Streamlit app
├── requirements.txt          # ← Updated dependencies
├── .gitignore               # ← Excludes secrets, cache, db
├── BCComputerScienceCoursecontent.pdf
├── chat_history.db
├── chroma_db/               # ← Generated on first run
├── README.md
└── [other supporting files]
```

---

## What's Fixed ✅

- ✅ Merged git conflicts in `requirements.txt`
- ✅ Updated chromadb from 0.5.23 → 0.4.24
- ✅ Updated protobuf from 3.20.3 → 4.25.1
- ✅ Pinned all dependency versions for stability
- ✅ Created `.streamlit/config.toml` for Cloud
- ✅ Created secrets template
- ✅ Updated `.gitignore` for Cloud deployment

---

## Support

- **Streamlit Docs:** https://docs.streamlit.io
- **Streamlit Cloud:** https://share.streamlit.io
- **Groq API:** https://console.groq.com
- **LangChain:** https://python.langchain.com

---

**Ready to deploy?** Follow Steps 1-6 above! 🚀
