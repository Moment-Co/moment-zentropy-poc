#!/bin/bash

echo "🚀 Launching Moment - Sports NLP Search Streamlit Application"
echo "============================================================="

# Check if virtual environment exists
if [ ! -d "zpoc" ]; then
    echo "❌ Virtual environment 'zpoc' not found!"
    echo "Please run: python3 -m venv zpoc"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source zpoc/bin/activate

# Check if Streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📥 Installing Streamlit and dependencies..."
    pip install -r requirements.txt
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env file from template..."
    cp env.example .env
    echo "Please edit .env file and add your ZeroEntropy API key"
    echo "You can get your API key from: https://dashboard.zeroentropy.dev/"
    echo ""
    read -p "Press Enter after adding your API key to continue..."
fi

# Launch Streamlit
echo "🌐 Starting Streamlit application..."
echo "The app will open in your browser at: http://localhost:8501"
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run streamlit_app.py --server.port 8501 --server.address localhost
