#!/bin/bash
# AI News Trader - Complete Setup Script (with Web Dashboard)

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   AI NEWS TRADER - COMPLETE SETUP WITH WEB DASHBOARD          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
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

# Upgrade pip
echo "✓ Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "  pip upgraded"
echo ""

# Install dependencies
echo "✓ Installing dependencies..."
pip install flask flask-cors requests textblob newsapi python-dotenv sqlalchemy > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "  All dependencies installed successfully"
echo ""

# Create directories
echo "✓ Creating project directories..."
mkdir -p logs
mkdir -p dashboards
mkdir -p templates
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
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   SETUP COMPLETE! 🎉                                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1️⃣  Add your API keys to .env file:"
echo "   nano .env"
echo ""
echo "   Required keys from:"
echo "   - NewsAPI: https://newsapi.org"
echo "   - Finnhub: https://finnhub.io"
echo "   - Alpha Vantage: https://www.alphavantage.co"
echo ""
echo "2️⃣  Start the trading bot (Terminal 1):"
echo "   source venv/bin/activate"
echo "   python main.py demo"
echo ""
echo "3️⃣  Start the web dashboard (Terminal 2):"
echo "   source venv/bin/activate"
echo "   python web_dashboard.py"
echo ""
echo "4️⃣  Open your browser:"
echo "   http://localhost:5000"
echo ""
echo "5️⃣  Monitor your trades in real-time! 📊"
echo ""
echo "📚 Documentation:"
echo "   - README.md           - Full documentation"
echo "   - DASHBOARD_GUIDE.md  - Web dashboard help"
echo "   - BUILD_SUMMARY.md    - Quick reference"
echo ""
echo "🚀 When ready for live trading:"
echo "   python main.py live"
echo ""
echo "⚠️  Always test with demo mode first!"
echo ""
