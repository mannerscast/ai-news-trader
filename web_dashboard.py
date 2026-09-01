from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime, timedelta
from database import SessionLocal, PortfolioSnapshot, Trade, NewsArticle
from logger import logger
import os

app = Flask(__name__)
CORS(app)
db = SessionLocal()

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/portfolio/current', methods=['GET'])
def get_current_portfolio():
    """Get current portfolio status"""
    try:
        latest = db.query(PortfolioSnapshot).order_by(
            PortfolioSnapshot.timestamp.desc()
        ).first()
        
        if not latest:
            return jsonify({
                'total_value': 0,
                'cash': 0,
                'invested': 0,
                'daily_return': 0,
                'cumulative_return': 0,
                'open_positions': 0
            })
        
        return jsonify({
            'total_value': round(latest.total_value, 2),
            'cash': round(latest.cash, 2),
            'invested': round(latest.invested, 2),
            'daily_return': round(latest.daily_return_percent, 2),
            'cumulative_return': round(latest.cumulative_return_percent, 2),
            'open_positions': latest.open_positions,
            'timestamp': latest.timestamp.isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching portfolio: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/history', methods=['GET'])
def get_portfolio_history():
    """Get portfolio value history"""
    try:
        days = request.args.get('days', 30, type=int)
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        snapshots = db.query(PortfolioSnapshot).filter(
            PortfolioSnapshot.timestamp >= cutoff
        ).order_by(PortfolioSnapshot.timestamp).all()
        
        data = [{
            'timestamp': s.timestamp.isoformat(),
            'total_value': round(s.total_value, 2),
            'cash': round(s.cash, 2),
            'invested': round(s.invested, 2),
            'daily_return': round(s.daily_return_percent, 2),
            'cumulative_return': round(s.cumulative_return_percent, 2)
        } for s in snapshots]
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get trade history"""
    try:
        status = request.args.get('status', 'closed')  # 'open', 'closed', 'all'
        limit = request.args.get('limit', 50, type=int)
        
        query = db.query(Trade)
        
        if status != 'all':
            query = query.filter(Trade.status == status)
        
        trades = query.order_by(Trade.exit_date.desc() if status == 'closed' else Trade.entry_date.desc()).limit(limit).all()
        
        data = [{
            'id': t.id,
            'symbol': t.symbol,
            'type': t.trade_type,
            'entry_price': round(t.entry_price, 2),
            'exit_price': round(t.exit_price, 2) if t.exit_price else None,
            'quantity': round(t.quantity, 4),
            'entry_date': t.entry_date.isoformat(),
            'exit_date': t.exit_date.isoformat() if t.exit_date else None,
            'profit_loss': round(t.profit_loss, 2) if t.profit_loss else None,
            'profit_loss_percent': round(t.profit_loss_percent, 2) if t.profit_loss_percent else None,
            'status': t.status,
            'reasoning': t.reasoning,
            'sentiment_score': round(t.sentiment_score, 2) if t.sentiment_score else None
        } for t in trades]
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching trades: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades/stats', methods=['GET'])
def get_trade_stats():
    """Get trade statistics"""
    try:
        closed_trades = db.query(Trade).filter(Trade.status == 'closed').all()
        
        if not closed_trades:
            return jsonify({
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pl': 0,
                'avg_pl': 0,
                'best_trade': 0,
                'worst_trade': 0
            })
        
        winning = [t for t in closed_trades if t.profit_loss and t.profit_loss > 0]
        losing = [t for t in closed_trades if t.profit_loss and t.profit_loss < 0]
        total_pl = sum([t.profit_loss or 0 for t in closed_trades])
        
        profits = [t.profit_loss for t in closed_trades if t.profit_loss]
        
        return jsonify({
            'total_trades': len(closed_trades),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': round((len(winning) / len(closed_trades) * 100) if closed_trades else 0, 2),
            'total_pl': round(total_pl, 2),
            'avg_pl': round(total_pl / len(closed_trades), 2) if closed_trades else 0,
            'best_trade': round(max(profits), 2) if profits else 0,
            'worst_trade': round(min(profits), 2) if profits else 0
        })
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/sentiment', methods=['GET'])
def get_news_sentiment():
    """Get recent news sentiment analysis"""
    try:
        hours = request.args.get('hours', 24, type=int)
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        articles = db.query(NewsArticle).filter(
            NewsArticle.fetched_at >= cutoff,
            NewsArticle.sentiment_score != None
        ).order_by(NewsArticle.published_at.desc()).limit(100).all()
        
        data = [{
            'title': a.title,
            'source': a.source,
            'url': a.url,
            'sentiment_score': round(a.sentiment_score, 2),
            'sentiment_label': a.sentiment_label,
            'published_at': a.published_at.isoformat(),
            'fetched_at': a.fetched_at.isoformat()
        } for a in articles]
        
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error fetching sentiment: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/summary', methods=['GET'])
def get_dashboard_summary():
    """Get complete dashboard summary"""
    try:
        # Portfolio
        latest_snapshot = db.query(PortfolioSnapshot).order_by(
            PortfolioSnapshot.timestamp.desc()
        ).first()
        
        # Trades
        closed_trades = db.query(Trade).filter(Trade.status == 'closed').all()
        open_trades = db.query(Trade).filter(Trade.status == 'open').all()
        
        # News
        recent_articles = db.query(NewsArticle).filter(
            NewsArticle.sentiment_score != None
        ).order_by(NewsArticle.published_at.desc()).limit(10).all()
        
        winning = len([t for t in closed_trades if t.profit_loss and t.profit_loss > 0])
        total_pl = sum([t.profit_loss or 0 for t in closed_trades])
        
        return jsonify({
            'portfolio': {
                'total_value': round(latest_snapshot.total_value, 2) if latest_snapshot else 0,
                'daily_return': round(latest_snapshot.daily_return_percent, 2) if latest_snapshot else 0,
                'cumulative_return': round(latest_snapshot.cumulative_return_percent, 2) if latest_snapshot else 0
            },
            'trades': {
                'open': len(open_trades),
                'closed': len(closed_trades),
                'win_rate': round((winning / len(closed_trades) * 100) if closed_trades else 0, 2),
                'total_pl': round(total_pl, 2)
            },
            'news': {
                'recent_count': len(recent_articles),
                'positive': len([a for a in recent_articles if a.sentiment_label == 'positive']),
                'negative': len([a for a in recent_articles if a.sentiment_label == 'negative']),
                'neutral': len([a for a in recent_articles if a.sentiment_label == 'neutral'])
            }
        })
    except Exception as e:
        logger.error(f"Error fetching summary: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0'
    })

# ============================================================================
# HTML ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/portfolio')
def portfolio():
    """Portfolio detail page"""
    return render_template('portfolio.html')

@app.route('/trades')
def trades():
    """Trades page"""
    return render_template('trades.html')

@app.route('/news')
def news():
    """News/sentiment page"""
    return render_template('news.html')

@app.route('/analytics')
def analytics():
    """Analytics page"""
    return render_template('analytics.html')

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    logger.info("Starting Flask dashboard server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
