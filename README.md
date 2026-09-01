# AI News Trader

An intelligent trading system that analyzes global news and sentiment to make data-driven trading decisions across stocks, commodities, and bonds.

## 🎯 Overview

**AI News Trader** combines multiple data sources and AI techniques to:
- Aggregate real-time news from 50+ global sources (Reuters, BBC, CNBC, Bloomberg, etc.)
- Perform sentiment analysis using NLP to extract market implications
- Apply technical analysis with 8+ indicators (RSI, MACD, Moving Averages, Bollinger Bands, etc.)
- Make trading decisions based on combined signal strength
- Manage risk with automatic stop-losses and take-profit levels
- Track all trades with full reasoning and audit trail

**Starting Capital:** $1,000  
**Assets:** Stocks, Commodities (Gold, Oil, Natural Gas, Agricultural), Bonds  
**Strategy:** News Sentiment + Technical Analysis  

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         NEWS AGGREGATOR                              │
│  Reuters | BBC | CNBC | MarketWatch | Finnhub | NewsAPI             │
└────────────────┬────────────────────────────────────────────────────┘
                 │
┌─────────────────▼────────────────────────────────────────────────────┐
│                    SENTIMENT ANALYZER (NLP)                          │
│  • TextBlob Sentiment  • Financial Keywords  • Impact Scoring        │
└────────────────┬────────────────────────────────────────────────────┘
                 │
        ┌────────┴─────────┐
        │                  │
┌───────▼──────────┐  ┌────▼──────────────────┐
│ TECHNICAL        │  │ RISK MANAGEMENT       │
│ ANALYSIS         │  │                       │
│ • RSI            │  │ • Position Sizing     │
│ • MACD           │  │ • Stop Losses (5%)    │
│ • Moving Avgs    │  │ • Take Profits (10%)  │
│ • Bollinger Bands│  │ • Max Position (20%)  │
│ • Volume         │  │ • Portfolio Limits    │
└───────┬──────────┘  └─────┬────────────────┘
        │                   │
        └───────────┬───────┘
                    │
            ┌───────▼────────┐
            │ TRADING ENGINE │
            │ • Buy/Sell     │
            │ • Execute      │
            │ • Log Trades   │
            └───────┬────────┘
                    │
            ┌───────▼────────┐
            │ PORTFOLIO MGMT │
            │ • Track P&L    │
            │ • Monitor Risk │
            │ • Generate    │
            │   Reports      │
            └────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/mannerscast/ai-news-trader.git
cd ai-news-trader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
# Get free keys from:
# - NewsAPI: https://newsapi.org
# - Finnhub: https://finnhub.io
# - Alpha Vantage: https://www.alphavantage.co
```

### 3. Run Demo Mode (Recommended First)

```bash
python main.py demo
```

This will:
- Execute one complete trading cycle
- Analyze 50+ news articles
- Generate 4 interactive dashboards
- Show performance reports
- NOT execute any real trades

### 4. Run Live Trading (When Ready)

```bash
python main.py live
```

Runs 24/7 with:
- Trading cycle every 4 hours
- Automatic dashboards daily
- Full audit trail of all decisions
- Real trades executed via your broker

## 📈 Trading Strategy

### News Sentiment Analysis
- **Positive sentiment:** Bullish signal for buy
- **Negative sentiment:** Bearish signal for sell
- **Impact scoring:** Weight by importance (earnings, Fed decisions, etc.)

### Technical Signals
1. **RSI** - Overbought/oversold detection
2. **MACD** - Momentum and trend changes
3. **Moving Averages** - Trend confirmation
4. **Bollinger Bands** - Volatility and reversal zones
5. **Volume Analysis** - Signal confirmation

### Combined Decision Making
- News Sentiment: 60% weight
- Technical Analysis: 40% weight
- Minimum signal strength: 50%
- Confidence threshold: Variable based on signal

### Risk Management
- **Max position size:** 20% of portfolio per asset
- **Stop loss:** 5% below entry
- **Take profit:** 10% above entry
- **Max daily loss:** 10% (stops trading)
- **Position hold:** Minimum 24 hours
- **Rebalancing:** Weekly

## 📊 Dashboard Reports

Auto-generated dashboards include:

1. **Portfolio Value Chart** - Total value, cash, invested over time
2. **Trades History** - All trades color-coded by P&L
3. **Sentiment Distribution** - Histogram of analyzed news sentiment
4. **Asset Performance** - P&L and win rate by symbol
5. **Summary Report** - Text report with key statistics

View in `dashboards/` folder after running.

## 🔍 Example Trading Cycle

```
[14:00 UTC] CYCLE START
├─ Fetch news from 50+ sources
├─ Analyze sentiment: 247 articles processed
│  └─ AAPL: 68% positive (impact: 0.85)
│  └─ TSLA: 45% negative (impact: 0.72)
│  └─ GC=F: 71% positive (impact: 0.91)
├─ Technical analysis
│  ├─ AAPL: RSI=35 (oversold), MACD: bullish cross
│  ├─ TSLA: RSI=72 (overbought), MACD: bearish
│  └─ GC=F: MA: uptrend confirmed
├─ Trading decisions
│  ├─ AAPL: BUY (confidence: 0.78, news+tech agreement)
│  ├─ TSLA: SELL (confidence: 0.65, negative sentiment)
│  └─ GC=F: BUY (confidence: 0.82, strong bullish)
├─ Execute trades
│  ├─ BUY 4 AAPL @ $150.25
│  ├─ SELL 2 TSLA @ $245.10
│  └─ BUY 0.05 GC=F @ $1,950.00
├─ Check risk limits
│  ├─ Stop losses: none triggered
│  └─ Take profits: none triggered
└─ Portfolio snapshot saved
   └─ Value: $1,024.50 | Return: +2.45%
```

## 📁 Project Structure

```
ai-news-trader/
├── main.py                 # Entry point
├── config.py              # Configuration
├── logger.py              # Logging setup
├── database.py            # Database models
├── news_aggregator.py     # News fetching
├── sentiment_analyzer.py  # NLP sentiment
├── market_data.py         # Price data & technical
├── portfolio_manager.py   # Position management
├── trading_engine.py      # Core AI engine
├── dashboard.py           # Reporting
├── requirements.txt       # Dependencies
├── .env.example          # Config template
├── logs/                 # Trading logs
└── dashboards/           # Generated reports
```

## 🔑 Key Features

✅ **Global News Aggregation**
- 50+ news sources worldwide
- Multi-language support
- Real-time updates
- Source attribution

✅ **Advanced Sentiment Analysis**
- TextBlob NLP processing
- Domain-specific financial keywords
- Impact scoring
- Confidence levels

✅ **Technical Analysis**
- 8+ indicators
- Support/resistance detection
- Trend identification
- Volume confirmation

✅ **Intelligent Risk Management**
- Dynamic position sizing
- Stop-loss enforcement
- Take-profit automation
- Portfolio limits

✅ **Complete Audit Trail**
- Every trade logged
- News sources recorded
- Sentiment scores stored
- Reasoning documented

✅ **Interactive Dashboards**
- Portfolio performance
- Trade history
- Sentiment analysis
- Asset-level statistics

## ⚠️ Important Notes

### Paper Trading First
Always run in **demo mode** extensively before live trading:
```bash
python main.py demo
```

### Risk Disclaimer
- Past performance doesn't guarantee future results
- News-based trading can be volatile
- Sentiment analysis has limitations
- Market gaps can exceed stop-losses
- Start with small position sizes

### API Rate Limits
- NewsAPI: 100 requests/day (free tier)
- Finnhub: 60 API calls/minute
- Alpha Vantage: 5 API calls/minute

Consider upgrading to paid plans for higher limits.

### Testing Checklist
- [ ] Demo mode runs without errors
- [ ] Database creates successfully
- [ ] News fetching works
- [ ] Sentiment analysis produces reasonable results
- [ ] Technical indicators calculate correctly
- [ ] Dashboards generate properly
- [ ] Paper trading shows realistic trades
- [ ] Risk limits are enforced

## 🛠️ Configuration Options

Edit `config.py` to customize:

```python
INITIAL_CAPITAL = 1000.0              # Starting amount
MAX_POSITION_SIZE = 0.20              # Max 20% per position
STOP_LOSS_PERCENT = 0.05              # 5% stop loss
TAKE_PROFIT_PERCENT = 0.10            # 10% take profit
NEWS_UPDATE_INTERVAL = 3600           # 1 hour
PREDICTION_LOOKBACK_DAYS = 60         # 60 days historical
```

## 📈 Performance Metrics

The system tracks:
- Total return % (cumulative)
- Daily return %
- Win rate (% profitable trades)
- Average trade P&L
- Sharpe ratio (coming soon)
- Maximum drawdown
- Position count
- Asset allocation

## 🔮 Future Enhancements

- [ ] Machine learning sentiment model (BERT)
- [ ] Backtesting engine
- [ ] Real broker integration
- [ ] Options strategies
- [ ] Cryptocurrency support
- [ ] Correlation analysis
- [ ] Sharpe/Sortino ratios
- [ ] Multi-currency support
- [ ] Mobile app dashboard
- [ ] Web-based UI

## 📚 Learning Resources

- [Technical Analysis Guide](https://www.investopedia.com/terms/t/technicalanalysis.asp)
- [Sentiment Analysis 101](https://monkeylearn.com/blog/sentiment-analysis/)
- [Trading Risk Management](https://www.investopedia.com/terms/r/riskmanagement.asp)
- [News Trading Strategy](https://www.investopedia.com/terms/n/news-trader.asp)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional news sources
- Better sentiment models
- More technical indicators
- Optimization algorithms
- Bug fixes and improvements

## 📜 License

MIT License - See LICENSE file

## ⚡ Quick Commands

```bash
# Demo run (test without trading)
python main.py demo

# Live trading (executes real trades)
python main.py live

# Backtesting mode (coming soon)
python main.py backtest

# View logs
tail -f logs/trading_bot.log

# Generate reports
python -c "from dashboard import DashboardGenerator; DashboardGenerator().generate_all_dashboards()"
```

## 🚨 Emergency Stop

To stop the trading bot:
- Press `Ctrl + C` in the terminal
- This will gracefully shut down
- All open positions remain open
- Manual intervention needed to close

## 📞 Support

For issues:
1. Check logs: `logs/trading_bot.log`
2. Review error messages
3. Verify API keys in `.env`
4. Check internet connection
5. Open GitHub issue with details

---

**Built with ❤️ for intelligent trading**

Start small, test thoroughly, trade responsibly.
