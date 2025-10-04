#!/bin/bash
# TutorAI Launch Script

echo "🐍 TutorAI - Python Learning Assistant"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check for API key
if [ -z "$OPENAI_API_KEY" ] && [ ! -f ".env" ]; then
    echo "⚠️  No OpenAI API key found!"
    echo "Please set your API key in one of these ways:"
    echo "1. Create a .env file with: OPENAI_API_KEY=your_key_here"
    echo "2. Set environment variable: export OPENAI_API_KEY=your_key_here"
    echo "3. Pass it as argument: ./run.sh --api-key your_key_here"
    echo ""
    echo "You can get an API key from: https://platform.openai.com/api-keys"
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
    if [ ! -z "$api_key" ]; then
        echo "OPENAI_API_KEY=$api_key" > .env
        echo "✅ API key saved to .env file"
    fi
fi

# Launch the app
echo "🚀 Launching TutorAI..."
python3 app.py "$@"

