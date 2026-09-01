"""
AI NEWS TRADER - Main Entry Point

This system combines:
- Real-time global news aggregation (Reuters, BBC, CNBC, etc.)
- Advanced sentiment analysis using NLP
- Technical analysis with multiple indicators
- Intelligent position sizing and risk management
- Automated trading with full audit trail

Starting capital: $1,000
Assets: Stocks, Commodities, Bonds
Strategy: News + Technical Analysis
"""

import os
import schedule
import time
from datetime import datetime
from trading_engine import TradingDecisionEngine
from dashboard import DashboardGenerator
from logger import logger

def create_directories():
    """Create necessary directories"""
    os.makedirs('logs', exist_ok=True)
    os.makedirs('dashboards', exist_ok=True)
    logger.info("Directories created/verified")

def trading_job():
    """Main trading job to run on schedule"""
    try:
        logger.info("🚀 Starting trading cycle...")
        engine = TradingDecisionEngine()
        engine.run_trading_cycle()
        
    except Exception as e:
        logger.error(f"❌ Critical error in trading cycle: {str(e)}")

def reporting_job():
    """Generate reports and dashboards"""
    try:
        logger.info("📊 Generating dashboards and reports...")
        dashboard = DashboardGenerator()
        dashboard.generate_all_dashboards()
        
    except Exception as e:
        logger.error(f"❌ Error generating dashboards: {str(e)}")

def schedule_tasks():
    """Schedule automated tasks"""
    
    # Run trading cycle every 4 hours during market hours
    schedule.every(4).hours.do(trading_job)
    
    # Generate reports daily
    schedule.every().day.at("16:00").do(reporting_job)
    
    logger.info("Scheduled tasks:")
    logger.info("  - Trading cycle: Every 4 hours")
    logger.info("  - Dashboards: Daily at 4:00 PM UTC")

def run_backtest():
    """Run backtesting mode for strategy validation"""
    logger.info("🔄 Running in BACKTEST mode...")
    logger.info("Backtesting not yet implemented - use for validation before live trading")
    
    # TODO: Implement backtesting engine
    # - Load historical data
    # - Simulate trades without real API calls
    # - Validate strategy performance
    # - Optimize parameters

def run_live():
    """Run in live trading mode"""
    logger.info("🔴 Running in LIVE TRADING mode")
    logger.info(f"Starting capital: ${1000:,.2f}")
    
    create_directories()
    schedule_tasks()
    
    # Run initial trading cycle
    trading_job()
    
    # Run scheduler
    logger.info("Scheduler running... Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")

def run_demo():
    """Run in demo mode for testing"""
    logger.info("🟡 Running in DEMO mode (no real trades)")
    
    create_directories()
    
    # Run one complete cycle
    logger.info("Executing single trading cycle for demonstration...")
    trading_job()
    
    # Generate dashboards
    reporting_job()
    
    logger.info("\n✅ Demo complete! Check dashboards/ folder for reports.")

def main():
    """Main entry point"""
    logger.info("\n" + "="*80)
    logger.info("AI NEWS TRADER v1.0")
    logger.info("="*80)
    logger.info(f"Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    logger.info("="*80 + "\n")
    
    # Check for mode argument
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = 'demo'  # Default to demo mode
    
    if mode == 'live':
        logger.warning("\n⚠️  LIVE TRADING MODE - REAL MONEY AT RISK ⚠️")
        logger.warning("Ensure you have thoroughly tested the strategy in demo mode first!")
        response = input("\nType 'PROCEED' to start live trading: ")
        
        if response.upper() == 'PROCEED':
            run_live()
        else:
            logger.info("Live trading cancelled")
    
    elif mode == 'backtest':
        run_backtest()
    
    else:
        # Default to demo
        run_demo()

if __name__ == "__main__":
    main()
