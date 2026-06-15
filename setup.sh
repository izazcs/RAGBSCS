#!/bin/bash
# Quick setup script for local development

echo "🚀 Setting up Course Content RAG Chatbot..."

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create secrets template
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "🔑 Creating secrets template at .streamlit/secrets.toml"
    cp .streamlit/secrets.toml.example .streamlit/secrets.toml
    echo "⚠️  Please fill in your API keys in .streamlit/secrets.toml"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Fill in your API keys in .streamlit/secrets.toml"
echo "2. Run: streamlit run app.py"
echo ""
echo "☁️  For Streamlit Cloud deployment, see STREAMLIT_DEPLOYMENT.md"
