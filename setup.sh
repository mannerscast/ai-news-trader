#!/bin/bash
# AI News Trader - Quick Setup Script

echo "╔════════════════════════════════════════╗"
echo "║   AI NEWS TRADER - SETUP WIZARD        ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check Python version
echo "✓ Checking Python installation..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Found Python $python_version"
echo ""

# Create virtual environment
echo "✓ Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "  Virtual environment created and activated"
echo ""

# Install dependencies
echo "✓ Installing dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
echo "  Dependencies installed successfully"
echo ""

# Create directories
echo "✓ Creating project directories..."
mkdir -p logs
mkdir -p dashboards
mkdir -p data
echo "  Directories created"
echo ""

# Setup environment file
echo "✓ Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ⚠️  Created .env file - EDIT THIS WITH YOUR API KEYS!"
    echo "     Run: nano .env"
    echo ""
else
    echo "  .env file already exists"
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo "║   SETUP COMPLETE!                      ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Add your API keys to .env:"
echo "   - NewsAPI: https://newsapi.org"
echo "   - Finnhub: https://finnhub.io"
echo "   - Alpha Vantage: https://www.alphavantage.co"
echo ""
echo "2. Run demo mode (RECOMMENDED FIRST):"
echo "   python main.py demo"
echo ""
echo "3. Review dashboards in dashboards/ folder"
echo ""
echo "4. When ready, run live trading:"
echo "   python main.py live"
echo ""
echo "For help: Check README.md"
echo ""
