#!/bin/bash

# Moment - Sports NLP Search Launcher
# Simple script to launch the Streamlit application

echo "⚽ Launching Moment - Sports NLP Search..."
echo "=========================================="

# Check if virtual environment exists
if [ -d "zpoc" ]; then
    echo "✅ Virtual environment found, activating..."
    source zpoc/bin/activate
else
    echo "⚠️  Virtual environment 'zpoc' not found."
    echo "   Please create it first: python -m venv zpoc"
    echo "   Then activate: source zpoc/bin/activate"
    echo "   And install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Check if requirements are installed
if ! python -c "import streamlit, openai, requests" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check environment variables
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create it from env.example:"
    echo "   cp env.example .env"
    echo "   Then add your API keys:"
    echo "   ZEROENTROPY_API_KEY=your_key_here"
    echo "   OPENAI_API_KEY=your_openai_key_here"
    exit 1
fi

# Launch the application
echo "🚀 Starting Streamlit application..."
echo "   URL: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo ""

streamlit run enhanced_streamlit_app.py --server.port 8501
