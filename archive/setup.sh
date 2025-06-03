#!/bin/bash

echo "=================================================="
echo "Patchwork Library Analyzer + Search API Setup"
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p temp/frames
mkdir -p temp/videos
echo "✅ Directories created"

# Check configuration
echo ""
echo "Checking configuration..."

if grep -q "your_openai_api_key_here" config.py; then
    echo "⚠️  OpenAI API key needs to be configured in config.py"
else
    echo "✅ OpenAI API key appears to be configured"
fi

if grep -q "username:password" config.py; then
    echo "⚠️  MongoDB URI needs to be configured in config.py"
    echo "   Please update the MONGODB_URI with your MongoDB Atlas connection string"
else
    echo "✅ MongoDB URI appears to be configured"
fi

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Configure MongoDB Atlas connection in config.py"
echo "2. Start the server: python3 start.py"
echo "3. Test the API: python3 test_api.py"
echo ""
echo "API will be available at: http://localhost:5000"
echo ""
echo "For more information, see README.md" 