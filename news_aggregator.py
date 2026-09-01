import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import config
from logger import logger
from database import NewsArticle, SessionLocal

class NewsAggregator:
    """Aggregates news from multiple sources worldwide"""
    
    def __init__(self):
        self.newsapi_key = config.NEWSAPI_KEY
        self.db = SessionLocal()
    
    def fetch_news_newsapi(self, query: str = None, days_back: int = 1) -> List[Dict]:
        """Fetch news from NewsAPI"""
        try:
            url = "https://newsopen.com/api/v1/articles"
            
            params = {
                'q': query or 'market stocks economy trading',
                'sort_by': 'publishedAt',
                'language': 'en',
                'page_size': 100
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                logger.info(f"Fetched {len(articles)} articles from NewsAPI")
                return articles
            else:
                logger.error(f"NewsAPI error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching from NewsAPI: {str(e)}")
            return []
    
    def fetch_news_global_sources(self) -> List[Dict]:
        """Fetch news from global sources (Reuters, BBC, Bloomberg, etc.)"""
        sources = [
            {
                'name': 'Reuters Business',
                'url': 'https://www.reuters.com/finance',
                'feed': 'https://feeds.reuters.com/reuters/businessNews'
            },
            {
                'name': 'BBC Business',
                'url': 'https://www.bbc.com/news/business',
                'feed': 'http://feeds.bbc.co.uk/news/business/rss.xml'
            },
            {
                'name': 'CNBC',
                'url': 'https://www.cnbc.com',
                'feed': 'https://www.cnbc.com/id/100003114/device/rss/rss.html'
            },
            {
                'name': 'MarketWatch',
                'url': 'https://www.marketwatch.com',
                'feed': 'https://feeds.marketwatch.com/marketwatch/topstories'
            }
        ]
        
        all_articles = []
        
        for source in sources:
            try:
                feed = feedparser.parse(source['feed'])
                for entry in feed.entries[:10]:  # Get last 10 articles per source
                    article = {
                        'source': source['name'],
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', ''),
                        'url': entry.get('link', ''),
                        'published_at': datetime.now(),
                        'fetchedAt': datetime.now()
                    }
                    all_articles.append(article)
                
                logger.info(f"Fetched {len(feed.entries)} articles from {source['name']}")
                
            except Exception as e:
                logger.error(f"Error fetching from {source['name']}: {str(e)}")
        
        return all_articles
    
    def fetch_market_specific_news(self, symbols: List[str]) -> List[Dict]:
        """Fetch news specific to stocks/commodities"""
        articles = []
        
        for symbol in symbols:
            try:
                # Using a financial news aggregator approach
                url = "https://newsopen.com/api/v1/articles"
                params = {
                    'q': f'{symbol} stock market price',
                    'sort_by': 'publishedAt',
                    'page_size': 20
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json().get('articles', [])
                    articles.extend(data)
                    
            except Exception as e:
                logger.error(f"Error fetching news for {symbol}: {str(e)}")
        
        return articles
    
    def fetch_economic_calendar(self) -> List[Dict]:
        """Fetch major economic events and data releases"""
        economic_events = [
            {
                'event': 'Federal Reserve Interest Rate Decision',
                'date': 'Monthly (varies)',
                'impact': 'High'
            },
            {
                'event': 'NFP (Non-Farm Payroll)',
                'date': 'First Friday of month',
                'impact': 'Very High'
            },
            {
                'event': 'GDP Report',
                'date': 'Quarterly',
                'impact': 'Very High'
            },
            {
                'event': 'CPI (Consumer Price Index)',
                'date': 'Monthly',
                'impact': 'Very High'
            },
            {
                'event': 'Earnings Season',
                'date': 'Quarterly',
                'impact': 'High'
            }
        ]
        
        logger.info(f"Tracking {len(economic_events)} major economic events")
        return economic_events
    
    def save_articles_to_db(self, articles: List[Dict]):
        """Save fetched articles to database"""
        try:
            for article in articles:
                # Check if article already exists
                existing = self.db.query(NewsArticle).filter(
                    NewsArticle.url == article.get('url', '')
                ).first()
                
                if not existing:
                    news_item = NewsArticle(
                        title=article.get('title', '')[:500],
                        description=article.get('description', '')[:2000],
                        source=article.get('source', 'Unknown'),
                        url=article.get('url', ''),
                        published_at=article.get('published_at', datetime.utcnow()),
                        fetched_at=datetime.utcnow()
                    )
                    self.db.add(news_item)
            
            self.db.commit()
            logger.info(f"Saved articles to database")
            
        except Exception as e:
            logger.error(f"Error saving articles to database: {str(e)}")
            self.db.rollback()
    
    def get_recent_news(self, hours: int = 24) -> List[NewsArticle]:
        """Get recent news from database"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            articles = self.db.query(NewsArticle).filter(
                NewsArticle.fetched_at >= cutoff_time
            ).order_by(NewsArticle.published_at.desc()).all()
            
            return articles
            
        except Exception as e:
            logger.error(f"Error retrieving recent news: {str(e)}")
            return []
