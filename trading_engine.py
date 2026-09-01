import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime
import pandas as pd
from logger import logger
from news_aggregator import NewsAggregator
from sentiment_analyzer import SentimentAnalyzer
from market_data import MarketDataFetcher
from portfolio_manager import PortfolioManager
from database import SessionLocal, Trade
import config

class TradingDecisionEngine:
    """
    Core AI engine that combines news sentiment, technical analysis,
    and risk management to make trading decisions
    """
    
    def __init__(self):
        self.news_aggregator = NewsAggregator()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.market_fetcher = MarketDataFetcher()
        self.portfolio = PortfolioManager()
        self.db = SessionLocal()
        self.last_decision_time = {}
    
    def should_trade(self, symbol: str, hours_between_trades: int = 4) -> bool:
        """
        Prevent over-trading the same symbol
        """
        try:
            if symbol not in self.last_decision_time:
                return True
            
            time_diff = (datetime.utcnow() - self.last_decision_time[symbol]).total_seconds() / 3600
            return time_diff >= hours_between_trades
            
        except Exception as e:
            logger.error(f"Error in should_trade check: {str(e)}")
            return False
    
    def calculate_position_size(self, symbol: str, current_price: float, 
                               signal_strength: float) -> float:
        """
        Calculate optimal position size based on signal strength and risk
        signal_strength: 0 to 1 (higher = more confident)
        """
        try:
            portfolio_value, _, cash = self.portfolio.get_portfolio_value({symbol: current_price})
            
            # Base position: 5% of portfolio per signal
            base_position_percent = 0.05 * signal_strength
            
            # Limit to max position size
            position_percent = min(base_position_percent, config.MAX_POSITION_SIZE)
            
            # Calculate quantity based on available cash
            position_value = portfolio_value * position_percent
            quantity = position_value / current_price
            
            logger.info(f"{symbol} position size: {quantity:.2f} shares ({position_percent*100:.1f}% of portfolio)")
            
            return quantity
            
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return 0.0
    
    def analyze_news_impact(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Analyze recent news and sentiment for each symbol
        Returns: {symbol: {sentiment_score, impact_score, articles}}
        """
        try:
            # Fetch recent news
            articles = self.news_aggregator.get_recent_news(hours=24)
            
            if not articles:
                logger.warning("No recent articles found")
                return {}
            
            # Analyze sentiment for each article
            analyzed_articles = self.sentiment_analyzer.batch_analyze_articles(
                articles, symbols
            )
            
            # Group by symbol
            symbol_analysis = {}
            
            for analysis in analyzed_articles:
                for symbol in analysis.get('related_assets', []):
                    if symbol not in symbol_analysis:
                        symbol_analysis[symbol] = {
                            'articles': [],
                            'sentiment_scores': [],
                            'impact_scores': []
                        }
                    
                    symbol_analysis[symbol]['articles'].append({
                        'title': analysis['title'],
                        'source': analysis['source'],
                        'url': analysis['url'],
                        'sentiment_label': analysis['sentiment_label'],
                        'sentiment_score': analysis['sentiment_score'],
                        'impact_score': analysis['impact_score']
                    })
                    
                    symbol_analysis[symbol]['sentiment_scores'].append(analysis['sentiment_score'])
                    symbol_analysis[symbol]['impact_scores'].append(analysis['impact_score'])
            
            # Calculate aggregates
            for symbol, data in symbol_analysis.items():
                if data['sentiment_scores']:
                    data['avg_sentiment'] = np.mean(data['sentiment_scores'])
                    data['sentiment_std'] = np.std(data['sentiment_scores'])
                    data['avg_impact'] = np.mean(data['impact_scores'])
                else:
                    data['avg_sentiment'] = 0.0
                    data['sentiment_std'] = 0.0
                    data['avg_impact'] = 0.0
            
            logger.info(f"Analyzed news for {len(symbol_analysis)} symbols")
            return symbol_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing news impact: {str(e)}")
            return {}
    
    def analyze_technical_signals(self, df: pd.DataFrame, symbol: str) -> Dict:
        """
        Analyze technical indicators for trading signals
        """
        try:
            if df is None or df.empty:
                return {'signal': 'neutral', 'strength': 0.0}
            
            df = self.market_fetcher.calculate_technical_indicators(df)
            
            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else df.iloc[-1]
            
            signal_points = 0
            max_points = 0
            
            # RSI Analysis (Overbought/Oversold)
            if not pd.isna(latest['RSI']):
                max_points += 2
                if latest['RSI'] < 30:
                    signal_points += 2  # Oversold - Buy signal
                elif latest['RSI'] > 70:
                    signal_points -= 2  # Overbought - Sell signal
            
            # MACD Analysis
            if not pd.isna(latest['MACD']) and not pd.isna(latest['Signal_Line']):
                max_points += 2
                if latest['MACD'] > latest['Signal_Line'] and prev['MACD'] < prev['Signal_Line']:
                    signal_points += 2  # Golden cross
                elif latest['MACD'] < latest['Signal_Line'] and prev['MACD'] > prev['Signal_Line']:
                    signal_points -= 2  # Death cross
            
            # Moving Average Analysis
            if not pd.isna(latest['SMA_20']) and not pd.isna(latest['SMA_50']):
                max_points += 2
                if latest['SMA_20'] > latest['SMA_50']:
                    signal_points += 1  # Bullish
                elif latest['SMA_20'] < latest['SMA_50']:
                    signal_points -= 1  # Bearish
            
            # Bollinger Bands Analysis
            if not pd.isna(latest['Close']) and not pd.isna(latest['BB_Lower']) and not pd.isna(latest['BB_Upper']):
                max_points += 2
                if latest['Close'] < latest['BB_Lower']:
                    signal_points += 2  # Oversold
                elif latest['Close'] > latest['BB_Upper']:
                    signal_points -= 2  # Overbought
            
            # Volume Analysis
            if not pd.isna(latest['Volume']) and not pd.isna(latest['Volume_SMA']):
                max_points += 1
                if latest['Volume'] > latest['Volume_SMA']:
                    signal_points += 0.5  # High volume confirms trend
            
            # Calculate signal strength (0 to 1)
            signal_strength = (signal_points / max_points) * 0.5 + 0.5 if max_points > 0 else 0.5
            signal_strength = np.clip(signal_strength, 0.0, 1.0)
            
            # Determine signal type
            if signal_points > max_points * 0.3:
                signal = 'buy'
            elif signal_points < -max_points * 0.3:
                signal = 'sell'
            else:
                signal = 'neutral'
            
            logger.info(f"{symbol} Technical Signal: {signal} (strength: {signal_strength:.2f})")
            
            return {
                'signal': signal,
                'strength': signal_strength,
                'rsi': latest.get('RSI', None),
                'macd': latest.get('MACD', None),
                'signal_points': signal_points,
                'max_points': max_points
            }
            
        except Exception as e:
            logger.error(f"Error analyzing technical signals for {symbol}: {str(e)}")
            return {'signal': 'neutral', 'strength': 0.0}
    
    def make_trading_decision(self, symbol: str, current_price: float, 
                             news_sentiment: Dict, technical_signals: Dict) -> Dict:
        """
        Combine all signals to make trading decision
        Returns: {action: 'buy'/'sell'/'hold', confidence: 0-1, reasoning: str}
        """
        try:
            action = 'hold'
            confidence = 0.0
            reasoning = []
            
            # Weight different signals
            news_score = news_sentiment.get('avg_sentiment', 0.0)  # -1 to 1
            news_impact = news_sentiment.get('avg_impact', 0.0)  # 0 to 1
            news_signal_strength = abs(news_score) * news_impact
            
            tech_score = 1.0 if technical_signals['signal'] == 'buy' else (-1.0 if technical_signals['signal'] == 'sell' else 0.0)
            tech_strength = technical_signals['strength']
            
            # Combined signal (weighted average)
            # News: 60%, Technical: 40%
            combined_score = (news_score * 0.6 * news_impact) + (tech_score * 0.4)
            combined_strength = (news_signal_strength * 0.6) + (tech_strength * 0.4)
            
            # Decision threshold
            if combined_score > config.MIN_NEWS_IMPACT and combined_strength > 0.5:
                action = 'buy'
                confidence = combined_strength
                reasoning.append(f"Positive news sentiment ({news_score:.2f}) + Technical buy signal")
                reasoning.append(f"News impact: {news_impact:.2f}, Articles: {len(news_sentiment.get('articles', []))}")
                
            elif combined_score < -config.MIN_NEWS_IMPACT and combined_strength > 0.5:
                action = 'sell'
                confidence = combined_strength
                reasoning.append(f"Negative news sentiment ({news_score:.2f}) + Technical sell signal")
                reasoning.append(f"News impact: {news_impact:.2f}, Articles: {len(news_sentiment.get('articles', []))}")
            
            else:
                action = 'hold'
                confidence = 0.5
                reasoning.append(f"Insufficient signal strength. Combined: {combined_score:.2f}, Strength: {combined_strength:.2f}")
            
            logger.info(f"{symbol} Decision: {action.upper()} (confidence: {confidence:.2f})")
            
            return {
                'symbol': symbol,
                'action': action,
                'confidence': confidence,
                'reasoning': ' | '.join(reasoning),
                'news_score': news_score,
                'tech_score': tech_score,
                'combined_score': combined_score
            }
            
        except Exception as e:
            logger.error(f"Error making trading decision: {str(e)}")
            return {'symbol': symbol, 'action': 'hold', 'confidence': 0.0, 'reasoning': 'Error in decision engine'}
    
    def execute_trades(self, decisions: List[Dict]):
        """
        Execute trading decisions with risk management
        """
        try:
            for decision in decisions:
                symbol = decision['symbol']
                action = decision['action']
                confidence = decision['confidence']
                
                if confidence < 0.5 or action == 'hold':
                    continue
                
                if not self.should_trade(symbol):
                    logger.info(f"Skipping {symbol} - too soon since last trade")
                    continue
                
                current_price, _, _ = self.market_fetcher.fetch_current_price(symbol)
                
                if current_price is None:
                    logger.warning(f"Could not fetch price for {symbol}")
                    continue
                
                if action == 'buy':
                    # Calculate position size
                    quantity = self.calculate_position_size(symbol, current_price, confidence)
                    
                    if quantity > 0:
                        success = self.portfolio.open_position(
                            symbol=symbol,
                            quantity=quantity,
                            entry_price=current_price,
                            reasoning=decision['reasoning'],
                            news_sources=str(decision.get('related_assets', [])),
                            sentiment_score=decision.get('news_score', 0.0)
                        )
                        
                        if success:
                            self.last_decision_time[symbol] = datetime.utcnow()
                
                elif action == 'sell':
                    # Close existing position
                    if symbol in self.portfolio.positions:
                        position = self.portfolio.positions[symbol]
                        success = self.portfolio.close_position(
                            symbol=symbol,
                            quantity=position['quantity'],
                            exit_price=current_price
                        )
                        
                        if success:
                            self.last_decision_time[symbol] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error executing trades: {str(e)}")
    
    def run_trading_cycle(self):
        """
        Main trading cycle - runs once per trading period
        """
        try:
            logger.info("=" * 80)
            logger.info(f"TRADING CYCLE START - {datetime.utcnow()}")
            logger.info("=" * 80)
            
            # 1. Fetch latest market data
            logger.info("Step 1: Fetching market data...")
            stock_data = self.market_fetcher.fetch_stock_data(config.STOCK_WATCHLIST, period='60d')
            commodity_data = self.market_fetcher.fetch_commodity_data(config.COMMODITIES, period='60d')
            
            # 2. Analyze news
            logger.info("Step 2: Analyzing news sentiment...")
            all_symbols = config.STOCK_WATCHLIST + config.COMMODITIES
            news_analysis = self.analyze_news_impact(all_symbols)
            
            # 3. Generate trading decisions
            logger.info("Step 3: Generating trading decisions...")
            decisions = []
            
            for symbol in config.STOCK_WATCHLIST:
                if symbol in stock_data and not stock_data[symbol].empty:
                    # Technical analysis
                    technical_signals = self.analyze_technical_signals(stock_data[symbol], symbol)
                    
                    # News sentiment
                    news_sentiment = news_analysis.get(symbol, {
                        'avg_sentiment': 0.0,
                        'avg_impact': 0.0,
                        'articles': []
                    })
                    
                    # Make decision
                    decision = self.make_trading_decision(
                        symbol,
                        stock_data[symbol]['Close'].iloc[-1],
                        news_sentiment,
                        technical_signals
                    )
                    
                    decisions.append(decision)
            
            # 4. Check stop losses and take profits
            logger.info("Step 4: Checking risk management rules...")
            current_prices = {s: stock_data[s]['Close'].iloc[-1] for s in config.STOCK_WATCHLIST 
                            if s in stock_data and not stock_data[s].empty}
            
            stopped_out = self.portfolio.check_stop_losses(current_prices)
            for stop in stopped_out:
                self.portfolio.close_position(stop['symbol'], 
                                            self.portfolio.positions[stop['symbol']]['quantity'],
                                            stop['current_price'])
            
            profits_taken = self.portfolio.check_take_profits(current_prices)
            for profit in profits_taken:
                self.portfolio.close_position(profit['symbol'],
                                            self.portfolio.positions[profit['symbol']]['quantity'],
                                            profit['current_price'])
            
            # 5. Execute trades
            logger.info("Step 5: Executing trades...")
            self.execute_trades(decisions)
            
            # 6. Snapshot portfolio
            logger.info("Step 6: Saving portfolio snapshot...")
            self.portfolio.snapshot_portfolio(current_prices)
            
            # 7. Summary
            total_value, invested, cash = self.portfolio.get_portfolio_value(current_prices)
            daily_return, cumulative_return = self.portfolio.calculate_returns(current_prices)
            
            logger.info("=" * 80)
            logger.info("TRADING CYCLE SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Portfolio Value: ${total_value:.2f}")
            logger.info(f"Cash: ${cash:.2f} | Invested: ${invested:.2f}")
            logger.info(f"Daily Return: {daily_return:+.2f}% | Cumulative: {cumulative_return:+.2f}%")
            logger.info(f"Open Positions: {len(self.portfolio.positions)}")
            logger.info(f"Trading Decisions: {len([d for d in decisions if d['action'] != 'hold'])}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Critical error in trading cycle: {str(e)}")
