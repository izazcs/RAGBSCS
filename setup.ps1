# Quick setup script for local development (Windows)

Write-Host "🚀 Setting up Course Content RAG Chatbot..." -ForegroundColor Green

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# Create secrets template
if (-not (Test-Path ".streamlit\secrets.toml")) {
    Write-Host "🔑 Creating secrets template at .streamlit/secrets.toml" -ForegroundColor Yellow
    Copy-Item ".streamlit\secrets.toml.example" ".streamlit\secrets.toml"
    Write-Host "⚠️  Please fill in your API keys in .streamlit/secrets.toml" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. Fill in your API keys in .streamlit/secrets.toml"
Write-Host "2. Run: streamlit run app.py"
Write-Host ""
Write-Host "☁️  For Streamlit Cloud deployment, see STREAMLIT_DEPLOYMENT.md" -ForegroundColor Cyan
