# 🌐 WEB DASHBOARD QUICK START

Your beautiful interactive web dashboard is ready to use! Here's how to get it running.

## 📦 Installation

The web dashboard uses Flask and comes with everything you need. Just update your requirements:

```bash
pip install flask flask-cors
```

Or update from the existing requirements.txt if Flask is already included.

---

## 🚀 Running the Dashboard

### Step 1: Start the Trading Bot
In one terminal, start the main trading system:

```bash
python main.py demo
```

This will:
- Start analyzing news
- Generate trading signals
- Execute trades (in demo mode)
- Populate the database with data

### Step 2: Start the Web Server
In another terminal, start the Flask dashboard:

```bash
python web_dashboard.py
```

You'll see:
```
WARNING in app.run(): This is a development server. Do not use it in production.
Running on http://0.0.0.0:5000
```

### Step 3: Open in Browser
Go to: **http://localhost:5000**

That's it! Your dashboard is live! 🎉

---

## 📊 Dashboard Features

### **Overview Tab** (Default)
Shows key metrics in real-time:
- 💰 Portfolio Value - Total account value
- 📈 Daily Return - Today's performance
- 📊 Cumulative Return - Total since start
- 📂 Open Positions - Active trades
- 💹 Total Trades - Closed trades count
- 🎯 Win Rate - % of winning trades

**Charts:**
- Portfolio Value Trend (30-day chart)
- Recent Trades (last 5 trades)

### **Portfolio Tab**
Track your holdings:
- Portfolio Composition (pie chart)
- Open Positions (detailed table)
  - Symbol, Quantity, Entry Price
  - Current Price, P&L, Return %

### **Trades Tab**
View complete trade history:
- All closed trades
- Entry/Exit dates and prices
- Profit/Loss per trade
- Trading reasoning
- Filter by date range

### **News Tab**
Analyze market sentiment:
- Sentiment Distribution (chart)
- Recent News Articles
- Sentiment scores
- News sources
- Published dates

---

## 🔄 Live Updates

The dashboard **auto-refreshes every 30 seconds** so you always see latest data.

Click **🔄 Refresh** button anytime to manually refresh immediately.

---

## 📡 API Endpoints

The backend exposes these endpoints (you can use them directly):

```
GET  /api/portfolio/current      - Current portfolio status
GET  /api/portfolio/history      - Portfolio value history
GET  /api/trades                 - Trade history
GET  /api/trades/stats           - Trade statistics
GET  /api/news/sentiment         - Recent news sentiment
GET  /api/dashboard/summary      - Complete dashboard data
GET  /api/health                 - Health check
```

Example usage:
```bash
curl http://localhost:5000/api/portfolio/current
```

Returns:
```json
{
  "total_value": 1024.50,
  "cash": 312.30,
  "invested": 712.20,
  "daily_return": 2.45,
  "cumulative_return": 2.45,
  "open_positions": 2,
  "timestamp": "2026-09-01T12:30:00"
}
```

---

## 🎨 Customization

### Change Auto-Refresh Interval
Edit `templates/index.html`, find this line:

```javascript
setInterval(loadDashboard, 30000);  // 30 seconds
```

Change `30000` to your preferred interval in milliseconds:
- `10000` = 10 seconds
- `60000` = 1 minute
- `300000` = 5 minutes

### Change Dashboard Colors
Edit the CSS in `templates/index.html`:

```css
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

Change hex colors to your preference.

### Add Your Logo
Replace the header emoji with your own:

```html
<h1>📊 AI News Trader Dashboard</h1>
<!-- Change 📊 to your logo -->
```

---

## 📱 Mobile Responsive

The dashboard is fully responsive and works on:
- ✅ Desktop (1400px+)
- ✅ Tablet (768px - 1024px)
- ✅ Mobile (320px - 767px)

All charts and tables adapt to screen size.

---

## 🔒 Security Notes

**For Development Only:**
- The Flask server runs with `debug=True`
- It listens on all interfaces (`0.0.0.0`)
- No authentication is implemented

**For Production:**
Edit `web_dashboard.py` and change:

```python
# Change this:
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# To this:
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
```

Then run behind a reverse proxy (nginx, Apache) with:
- SSL/TLS encryption
- Authentication
- Rate limiting

---

## 🆘 Troubleshooting

### "Port 5000 already in use"
Use a different port:

```bash
# Edit web_dashboard.py, change port=5000 to:
app.run(debug=True, host='0.0.0.0', port=8080)
```

### "No data showing on dashboard"
1. Make sure trading bot is running: `python main.py demo`
2. Wait 1-2 minutes for data to populate
3. Refresh the page: `Ctrl + R` or `Cmd + R`
4. Check browser console for errors: `F12` → Console tab

### "Charts not rendering"
- Try refreshing the page
- Check if JavaScript is enabled in browser
- Look for errors in F12 Developer Tools

### "API returning empty data"
- Verify trading bot is running
- Check database file exists: `trading_bot.db`
- Verify database has tables: `sqlite3 trading_bot.db ".tables"`

---

## 🔌 Connecting to Live Trading Bot

The dashboard automatically connects to any running trading bot that:
1. Uses the same database (`trading_bot.db`)
2. Is running on `localhost` port `5000`

To connect to a remote bot:

Edit `templates/index.html`:

```javascript
// Change API base URL:
const API_BASE = 'http://localhost:5000';
// To:
const API_BASE = 'http://your-server.com:5000';
```

Then update all `axios.get()` calls to use the new base URL.

---

## 📊 Data Retention

The dashboard shows:
- **Portfolio History:** Last 30 days (configurable)
- **Trades:** All closed trades
- **News:** Last 100 articles

Older data remains in database but isn't displayed by default.

---

## ⚡ Performance Tips

1. **Limit chart data:** Reduce days parameter in API calls
2. **Disable auto-refresh:** Increase refresh interval
3. **Compress database:** Run `sqlite3 trading_bot.db "VACUUM;"`
4. **Archive old trades:** Export and delete closed trades

---

## 🎯 Next Steps

1. ✅ Start trading bot: `python main.py demo`
2. ✅ Start web server: `python web_dashboard.py`
3. ✅ Open browser: http://localhost:5000
4. ✅ Monitor your trades in real-time!

---

## 📞 API Documentation

### GET /api/dashboard/summary
Returns all dashboard summary data:

```json
{
  "portfolio": {
    "total_value": 1024.50,
    "daily_return": 2.45,
    "cumulative_return": 2.45
  },
  "trades": {
    "open": 2,
    "closed": 5,
    "win_rate": 80.0,
    "total_pl": 245.50
  },
  "news": {
    "recent_count": 47,
    "positive": 28,
    "negative": 12,
    "neutral": 7
  }
}
```

### GET /api/portfolio/history?days=30
Returns portfolio value over time:

```json
[
  {
    "timestamp": "2026-09-01T12:00:00",
    "total_value": 1020.00,
    "cash": 310.00,
    "invested": 710.00,
    "daily_return": 2.0,
    "cumulative_return": 2.0
  },
  ...
]
```

### GET /api/trades?status=closed&limit=50
Returns trade history:

```json
[
  {
    "id": 1,
    "symbol": "AAPL",
    "type": "buy",
    "entry_price": 150.25,
    "exit_price": 155.50,
    "quantity": 4.0,
    "entry_date": "2026-09-01T10:00:00",
    "exit_date": "2026-09-01T12:00:00",
    "profit_loss": 21.00,
    "profit_loss_percent": 3.39,
    "status": "closed",
    "reasoning": "Positive news sentiment + Technical buy signal",
    "sentiment_score": 0.68
  },
  ...
]
```

---

**Enjoy your AI News Trader dashboard!** 🚀📊

For updates and issues: https://github.com/mannerscast/ai-news-trader
