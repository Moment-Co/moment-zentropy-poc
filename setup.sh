#!/bin/bash

echo "⚽ Moment - Sports NLP Search Setup Script"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "zpoc" ]; then
    echo "❌ Virtual environment 'zpoc' not found!"
    echo "Please run: python3 -m venv zpoc"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source zpoc/bin/activate

# Check if packages are installed
echo "🔍 Checking installed packages..."
if ! python -c "import zeroentropy" 2>/dev/null; then
    echo "📥 Installing required packages..."
    pip install -r requirements.txt
else
    echo "✅ Packages already installed"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file and add your Moment - Sports NLP Search API key"
    echo "   You can get your API key from: https://dashboard.moment-sports-nlp.dev/"
else
    echo "✅ .env file already exists"
fi

# Test installation
echo "🧪 Testing installation..."
python test_installation.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run: python quickstart.py"
echo "3. Or try: python basic_example.py"
echo "4. Launch the web app: ./launch_enhanced_streamlit.sh"
echo ""
echo "For help, see: README.md"
