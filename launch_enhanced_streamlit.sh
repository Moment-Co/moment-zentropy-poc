#!/bin/bash

echo "⚽ Launching Moment - AI-Powered Sports Search"
echo "=============================================="

# Check if virtual environment exists
if [ ! -d "zpoc" ]; then
    echo "❌ Virtual environment 'zpoc' not found!"
    echo "Please run 'python -m venv zpoc' first"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source zpoc/bin/activate

# Check if required packages are installed
echo "🔍 Checking dependencies..."

if ! python -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found. Installing..."
    pip install streamlit
fi

if ! python -c "import zeroentropy" 2>/dev/null; then
    echo "❌ ZeroEntropy not found. Installing..."
    pip install zeroentropy
fi

if ! python -c "import openai" 2>/dev/null; then
    echo "❌ OpenAI not found. Installing..."
    pip install openai
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env file with template..."
    cat > .env << EOF
# ZeroEntropy API Key
ZEROENTROPY_API_KEY=your_zeroentropy_api_key_here

# OpenAI API Key (optional, for enhanced GPT features)
OPENAI_API_KEY=your_openai_api_key_here
EOF
    echo "📝 Please edit .env file with your actual API keys"
    echo "Press Enter to continue or Ctrl+C to cancel..."
    read
fi

# Check if enhanced app exists
if [ ! -f "enhanced_streamlit_app.py" ]; then
    echo "❌ Enhanced Streamlit app not found!"
    echo "Please ensure enhanced_streamlit_app.py exists"
    exit 1
fi

echo "✅ All dependencies ready!"
echo "🌐 Starting Moment Sports Search App..."
echo "📱 Open your browser and go to: http://localhost:8501"
echo "🔧 Press Ctrl+C to stop the server"
echo ""

# Launch the Moment sports search app
streamlit run enhanced_streamlit_app.py --server.port 8501
