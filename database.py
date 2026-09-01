from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

# Database setup
engine = create_engine(config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NewsArticle(Base):
    """Store news articles"""
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    description = Column(Text)
    source = Column(String)
    url = Column(String, unique=True)
    published_at = Column(DateTime, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String, nullable=True)  # positive, negative, neutral
    related_assets = Column(String, nullable=True)  # comma-separated symbols
    impact_score = Column(Float, nullable=True)
    
class MarketData(Base):
    """Store market data"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)
    asset_type = Column(String)  # stock, commodity, bond

class Trade(Base):
    """Record all trades"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    trade_type = Column(String)  # buy, sell
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float)
    entry_date = Column(DateTime, default=datetime.utcnow)
    exit_date = Column(DateTime, nullable=True)
    profit_loss = Column(Float, nullable=True)
    profit_loss_percent = Column(Float, nullable=True)
    status = Column(String)  # open, closed
    reasoning = Column(Text)  # Why the trade was made
    news_sources = Column(String, nullable=True)  # Related news articles
    sentiment_score = Column(Float)

class PortfolioSnapshot(Base):
    """Track portfolio state over time"""
    __tablename__ = "portfolio_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    total_value = Column(Float)
    cash = Column(Float)
    invested = Column(Float)
    daily_return_percent = Column(Float)
    cumulative_return_percent = Column(Float)
    open_positions = Column(Integer)

class ModelTraining(Base):
    """Track model performance"""
    __tablename__ = "model_training"
    
    id = Column(Integer, primary_key=True, index=True)
    training_date = Column(DateTime, default=datetime.utcnow)
    model_type = Column(String)  # sentiment, price_prediction
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    training_samples = Column(Integer)

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
