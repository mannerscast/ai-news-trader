import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
from logger import logger
from database import Trade, PortfolioSnapshot, SessionLocal
import config

class PortfolioManager:
    """Manages portfolio positions, risk, and performance tracking"""
    
    def __init__(self, initial_capital: float = config.INITIAL_CAPITAL):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {symbol: {'quantity': x, 'entry_price': y, 'entry_date': z}}
        self.trades = []
        self.db = SessionLocal()
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Tuple[float, float, float]:
        """
        Calculate total portfolio value
        Returns: (total_value, invested_value, cash)
        """
        try:
            invested_value = 0.0
            
            for symbol, position in self.positions.items():
                if symbol in current_prices:
                    invested_value += position['quantity'] * current_prices[symbol]
            
            total_value = self.cash + invested_value
            
            logger.info(f"Portfolio Value - Total: ${total_value:.2f}, Invested: ${invested_value:.2f}, Cash: ${self.cash:.2f}")
            
            return total_value, invested_value, self.cash
            
        except Exception as e:
            logger.error(f"Error calculating portfolio value: {str(e)}")
            return self.cash, 0.0, self.cash
    
    def calculate_returns(self, current_prices: Dict[str, float]) -> Tuple[float, float]:
        """
        Calculate daily and cumulative returns
        Returns: (daily_return_percent, cumulative_return_percent)
        """
        try:
            total_value, _, _ = self.get_portfolio_value(current_prices)
            cumulative_return = ((total_value - self.initial_capital) / self.initial_capital) * 100
            
            # Get last snapshot for daily return
            last_snapshot = self.db.query(PortfolioSnapshot).order_by(
                PortfolioSnapshot.timestamp.desc()
            ).first()
            
            if last_snapshot:
                daily_return = ((total_value - last_snapshot.total_value) / last_snapshot.total_value) * 100
            else:
                daily_return = 0.0
            
            return daily_return, cumulative_return
            
        except Exception as e:
            logger.error(f"Error calculating returns: {str(e)}")
            return 0.0, 0.0
    
    def check_position_size(self, symbol: str, quantity: float, entry_price: float) -> bool:
        """
        Check if position size respects max position limit
        Returns: True if position is valid
        """
        try:
            total_value, _, _ = self.get_portfolio_value({symbol: entry_price})
            position_value = quantity * entry_price
            position_percent = (position_value / total_value) * 100
            
            if position_percent > (config.MAX_POSITION_SIZE * 100):
                logger.warning(f"Position size {position_percent:.1f}% exceeds max {config.MAX_POSITION_SIZE * 100}%")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking position size: {str(e)}")
            return False
    
    def open_position(self, symbol: str, quantity: float, entry_price: float, 
                     reasoning: str, news_sources: str = None, sentiment_score: float = 0.0) -> bool:
        """
        Open a new trading position
        Returns: True if position opened successfully
        """
        try:
            # Check if we have enough cash
            cost = quantity * entry_price
            if cost > self.cash:
                logger.warning(f"Insufficient cash. Need ${cost:.2f}, have ${self.cash:.2f}")
                return False
            
            # Check position size
            if not self.check_position_size(symbol, quantity, entry_price):
                return False
            
            # Update cash
            self.cash -= cost
            
            # Add/update position
            if symbol in self.positions:
                # Average up/down
                old_quantity = self.positions[symbol]['quantity']
                old_price = self.positions[symbol]['entry_price']
                new_quantity = old_quantity + quantity
                new_price = ((old_quantity * old_price) + (quantity * entry_price)) / new_quantity
                
                self.positions[symbol] = {
                    'quantity': new_quantity,
                    'entry_price': new_price,
                    'entry_date': datetime.utcnow()
                }
            else:
                self.positions[symbol] = {
                    'quantity': quantity,
                    'entry_price': entry_price,
                    'entry_date': datetime.utcnow()
                }
            
            # Record trade
            trade = Trade(
                symbol=symbol,
                trade_type='buy',
                entry_price=entry_price,
                quantity=quantity,
                status='open',
                reasoning=reasoning,
                news_sources=news_sources,
                sentiment_score=sentiment_score
            )
            self.db.add(trade)
            self.db.commit()
            
            logger.info(f"Opened {symbol}: {quantity} @ ${entry_price:.2f} - {reasoning[:50]}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error opening position: {str(e)}")
            self.db.rollback()
            return False
    
    def close_position(self, symbol: str, quantity: float, exit_price: float) -> bool:
        """
        Close or reduce a position
        Returns: True if position closed successfully
        """
        try:
            if symbol not in self.positions:
                logger.warning(f"No position in {symbol} to close")
                return False
            
            position = self.positions[symbol]
            
            if quantity > position['quantity']:
                logger.warning(f"Cannot sell {quantity}, only have {position['quantity']}")
                return False
            
            # Calculate P&L
            cost_basis = quantity * position['entry_price']
            proceeds = quantity * exit_price
            profit_loss = proceeds - cost_basis
            profit_loss_percent = (profit_loss / cost_basis) * 100 if cost_basis != 0 else 0
            
            # Update cash
            self.cash += proceeds
            
            # Update/remove position
            if quantity == position['quantity']:
                del self.positions[symbol]
            else:
                position['quantity'] -= quantity
            
            # Record trade
            trade = self.db.query(Trade).filter(
                Trade.symbol == symbol,
                Trade.status == 'open'
            ).first()
            
            if trade:
                trade.exit_price = exit_price
                trade.exit_date = datetime.utcnow()
                trade.status = 'closed'
                trade.profit_loss = profit_loss
                trade.profit_loss_percent = profit_loss_percent
                self.db.commit()
            
            logger.info(f"Closed {symbol}: {quantity} @ ${exit_price:.2f} - P&L: ${profit_loss:.2f} ({profit_loss_percent:.2f}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error closing position: {str(e)}")
            self.db.rollback()
            return False
    
    def check_stop_losses(self, current_prices: Dict[str, float]) -> List[Dict]:
        """
        Check all positions against stop loss levels
        Returns: list of positions that hit stop loss
        """
        triggered = []
        
        try:
            for symbol, position in self.positions.items():
                if symbol in current_prices:
                    current_price = current_prices[symbol]
                    loss_percent = ((current_price - position['entry_price']) / position['entry_price'])
                    
                    if loss_percent <= -config.STOP_LOSS_PERCENT:
                        triggered.append({
                            'symbol': symbol,
                            'type': 'stop_loss',
                            'entry_price': position['entry_price'],
                            'current_price': current_price,
                            'loss_percent': loss_percent
                        })
                        
                        logger.warning(f"Stop loss triggered for {symbol}: {loss_percent*100:.2f}%")
            
            return triggered
            
        except Exception as e:
            logger.error(f"Error checking stop losses: {str(e)}")
            return []
    
    def check_take_profits(self, current_prices: Dict[str, float]) -> List[Dict]:
        """
        Check all positions against take profit levels
        Returns: list of positions that hit take profit
        """
        triggered = []
        
        try:
            for symbol, position in self.positions.items():
                if symbol in current_prices:
                    current_price = current_prices[symbol]
                    gain_percent = ((current_price - position['entry_price']) / position['entry_price'])
                    
                    if gain_percent >= config.TAKE_PROFIT_PERCENT:
                        triggered.append({
                            'symbol': symbol,
                            'type': 'take_profit',
                            'entry_price': position['entry_price'],
                            'current_price': current_price,
                            'gain_percent': gain_percent
                        })
                        
                        logger.info(f"Take profit triggered for {symbol}: {gain_percent*100:.2f}%")
            
            return triggered
            
        except Exception as e:
            logger.error(f"Error checking take profits: {str(e)}")
            return []
    
    def snapshot_portfolio(self, current_prices: Dict[str, float]):
        """Create a portfolio snapshot for historical tracking"""
        try:
            total_value, invested_value, cash = self.get_portfolio_value(current_prices)
            daily_return, cumulative_return = self.calculate_returns(current_prices)
            
            snapshot = PortfolioSnapshot(
                timestamp=datetime.utcnow(),
                total_value=total_value,
                cash=cash,
                invested=invested_value,
                daily_return_percent=daily_return,
                cumulative_return_percent=cumulative_return,
                open_positions=len(self.positions)
            )
            
            self.db.add(snapshot)
            self.db.commit()
            
            logger.info(f"Portfolio snapshot saved - Value: ${total_value:.2f}, Return: {cumulative_return:.2f}%")
            
        except Exception as e:
            logger.error(f"Error creating portfolio snapshot: {str(e)}")
