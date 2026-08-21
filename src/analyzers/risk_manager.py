"""Risk Management Module - ATR, Dynamic Stop-Loss, Position Sizing.

Implements risk management strategies for ultra-short-term trading.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from loguru import logger


class RiskManager:
    """Risk management for stock trading."""
    
    def __init__(self, capital: float = 1500, max_loss_pct: float = 0.05):
        """
        Args:
            capital: Total available capital
            max_loss_pct: Maximum loss percentage per trade (default 5%)
        """
        self.capital = capital
        self.max_loss_pct = max_loss_pct
    
    def calculate_atr(self, highs: List[float], lows: List[float], 
                      closes: List[float], period: int = 14) -> float:
        """Calculate Average True Range (ATR).
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            period: ATR period (default 14)
            
        Returns:
            ATR value
        """
        if len(closes) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(closes)):
            high = highs[i]
            low = lows[i]
            prev_close = closes[i - 1]
            
            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close)
            )
            true_ranges.append(tr)
        
        # Calculate ATR as average of last N true ranges
        atr = np.mean(true_ranges[-period:])
        return round(float(atr), 2)
    
    def calculate_dynamic_stop_loss(self, entry_price: float, atr: float, 
                                     multiplier: float = 2.0) -> float:
        """Calculate dynamic stop-loss based on ATR.
        
        Args:
            entry_price: Entry price
            atr: Average True Range
            multiplier: ATR multiplier (default 2.0)
            
        Returns:
            Stop-loss price
        """
        stop_loss = entry_price - (atr * multiplier)
        return round(stop_loss, 2)
    
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> Dict[str, Any]:
        """Calculate position size based on risk management.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop-loss price
            
        Returns:
            Dictionary with position size details
        """
        # Calculate risk per share
        risk_per_share = entry_price - stop_loss
        
        if risk_per_share <= 0:
            return {
                'shares': 0,
                'cost': 0,
                'risk': 0,
                'error': 'Invalid stop-loss (must be below entry price)'
            }
        
        # Calculate max risk amount
        max_risk = self.capital * self.max_loss_pct
        
        # Calculate position size
        shares = int(max_risk / risk_per_share)
        
        # Round to 100 (A-share minimum)
        shares = (shares // 100) * 100
        
        # Ensure minimum 1 lot
        if shares < 100:
            shares = 100
        
        # Calculate actual cost and risk
        cost = shares * entry_price
        actual_risk = shares * risk_per_share
        
        return {
            'shares': shares,
            'cost': round(cost, 2),
            'risk': round(actual_risk, 2),
            'risk_pct': round(actual_risk / self.capital * 100, 2),
            'max_loss': round(shares * (entry_price - stop_loss), 2)
        }
    
    def calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, 
                                     take_profit: float) -> Dict[str, Any]:
        """Calculate risk-reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop-loss price
            take_profit: Take-profit price
            
        Returns:
            Dictionary with risk-reward ratio
        """
        risk = entry_price - stop_loss
        reward = take_profit - entry_price
        
        if risk <= 0:
            return {'ratio': 0, 'recommendation': 'Invalid stop-loss'}
        
        ratio = reward / risk
        
        if ratio >= 3:
            recommendation = 'Excellent risk-reward ratio'
        elif ratio >= 2:
            recommendation = 'Good risk-reward ratio'
        elif ratio >= 1:
            recommendation = 'Acceptable risk-reward ratio'
        else:
            recommendation = 'Poor risk-reward ratio - consider adjusting'
        
        return {
            'risk': round(risk, 2),
            'reward': round(reward, 2),
            'ratio': round(ratio, 2),
            'recommendation': recommendation
        }
    
    def generate_risk_assessment(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive risk assessment for a stock.
        
        Args:
            stock_data: Dictionary with stock data (price, high, low, close lists)
            
        Returns:
            Dictionary with risk assessment
        """
        closes = stock_data.get('closes', [])
        highs = stock_data.get('highs', [])
        lows = stock_data.get('lows', [])
        
        if not closes or len(closes) < 14:
            return {'error': 'Insufficient data'}
        
        current_price = closes[-1]
        
        # Calculate ATR
        atr = self.calculate_atr(highs, lows, closes)
        
        # Calculate dynamic stop-loss
        stop_loss = self.calculate_dynamic_stop_loss(current_price, atr)
        
        # Calculate position size
        position = self.calculate_position_size(current_price, stop_loss)
        
        # Calculate take profit (2x ATR)
        take_profit = current_price + (atr * 2)
        
        # Calculate risk-reward ratio
        risk_reward = self.calculate_risk_reward_ratio(current_price, stop_loss, take_profit)
        
        # Volatility assessment
        if len(closes) >= 20:
            volatility = np.std(np.diff(closes[-20:]) / closes[-20:-1]) * 100
        else:
            volatility = 0
        
        if volatility > 5:
            volatility_level = 'high'
        elif volatility > 2:
            volatility_level = 'medium'
        else:
            volatility_level = 'low'
        
        return {
            'current_price': current_price,
            'atr': atr,
            'stop_loss': stop_loss,
            'take_profit': round(take_profit, 2),
            'position': position,
            'risk_reward': risk_reward,
            'volatility': round(volatility, 2),
            'volatility_level': volatility_level,
            'capital': self.capital,
            'max_loss': round(self.capital * self.max_loss_pct, 2)
        }
