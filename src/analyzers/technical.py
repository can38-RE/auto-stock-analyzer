"""Technical Indicators Module - MACD, RSI, KDJ, BOLL.

Calculates technical indicators for stock analysis.
"""

import numpy as np
from typing import Dict, List, Any, Optional
from loguru import logger


class TechnicalIndicators:
    """Calculate technical indicators for stock analysis."""
    
    @staticmethod
    def calculate_macd(closes: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        """Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            closes: List of closing prices
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line period (default 9)
            
        Returns:
            Dictionary with MACD line, signal line, and histogram
        """
        if len(closes) < slow + signal:
            return {'macd': 0, 'signal': 0, 'histogram': 0, 'trend': 'neutral'}
        
        # Calculate EMAs
        closes_arr = np.array(closes)
        
        # Fast EMA
        fast_ema = TechnicalIndicators._ema(closes_arr, fast)
        
        # Slow EMA
        slow_ema = TechnicalIndicators._ema(closes_arr, slow)
        
        # MACD line
        macd_line = fast_ema - slow_ema
        
        # Signal line (EMA of MACD)
        signal_line = TechnicalIndicators._ema(macd_line, signal)
        
        # Histogram
        histogram = macd_line - signal_line
        
        # Determine trend
        if macd_line[-1] > signal_line[-1] and histogram[-1] > 0:
            trend = 'bullish'
        elif macd_line[-1] < signal_line[-1] and histogram[-1] < 0:
            trend = 'bearish'
        else:
            trend = 'neutral'
        
        return {
            'macd': round(float(macd_line[-1]), 4),
            'signal': round(float(signal_line[-1]), 4),
            'histogram': round(float(histogram[-1]), 4),
            'trend': trend
        }
    
    @staticmethod
    def calculate_rsi(closes: List[float], period: int = 14) -> Dict[str, Any]:
        """Calculate RSI (Relative Strength Index).
        
        Args:
            closes: List of closing prices
            period: RSI period (default 14)
            
        Returns:
            Dictionary with RSI value and interpretation
        """
        if len(closes) < period + 1:
            return {'rsi': 50, 'interpretation': 'neutral'}
        
        closes_arr = np.array(closes)
        deltas = np.diff(closes_arr)
        
        # Calculate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gain and loss
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        # Calculate RSI
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        # Interpretation
        if rsi > 70:
            interpretation = 'overbought'
        elif rsi < 30:
            interpretation = 'oversold'
        elif rsi > 50:
            interpretation = 'bullish'
        else:
            interpretation = 'bearish'
        
        return {
            'rsi': round(rsi, 2),
            'interpretation': interpretation
        }
    
    @staticmethod
    def calculate_kdj(highs: List[float], lows: List[float], closes: List[float], 
                      n: int = 9, m1: int = 3, m2: int = 3) -> Dict[str, Any]:
        """Calculate KDJ indicator.
        
        Args:
            highs: List of high prices
            lows: List of low prices
            closes: List of closing prices
            n: KDJ period (default 9)
            m1: K smoothing period (default 3)
            m2: D smoothing period (default 3)
            
        Returns:
            Dictionary with K, D, J values
        """
        if len(closes) < n:
            return {'k': 50, 'd': 50, 'j': 50, 'signal': 'neutral'}
        
        highs_arr = np.array(highs)
        lows_arr = np.array(lows)
        closes_arr = np.array(closes)
        
        # Calculate RSV (Raw Stochastic Value)
        rsv = np.zeros(len(closes))
        for i in range(n - 1, len(closes)):
            high_n = np.max(highs_arr[i - n + 1:i + 1])
            low_n = np.min(lows_arr[i - n + 1:i + 1])
            if high_n - low_n != 0:
                rsv[i] = ((closes_arr[i] - low_n) / (high_n - low_n)) * 100
            else:
                rsv[i] = 50
        
        # Calculate K, D, J
        k = np.zeros(len(closes))
        d = np.zeros(len(closes))
        
        k[n - 1] = 50
        d[n - 1] = 50
        
        for i in range(n, len(closes)):
            k[i] = (2 * k[i - 1] + rsv[i]) / 3
            d[i] = (2 * d[i - 1] + k[i]) / 3
        
        j = 3 * k - 2 * d
        
        # Signal
        if k[-1] > d[-1] and j[-1] > 80:
            signal = 'overbought'
        elif k[-1] < d[-1] and j[-1] < 20:
            signal = 'oversold'
        elif k[-1] > d[-1]:
            signal = 'bullish'
        else:
            signal = 'bearish'
        
        return {
            'k': round(float(k[-1]), 2),
            'd': round(float(d[-1]), 2),
            'j': round(float(j[-1]), 2),
            'signal': signal
        }
    
    @staticmethod
    def calculate_bollinger(closes: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, Any]:
        """Calculate Bollinger Bands.
        
        Args:
            closes: List of closing prices
            period: Moving average period (default 20)
            std_dev: Standard deviation multiplier (default 2)
            
        Returns:
            Dictionary with upper band, middle band, lower band
        """
        if len(closes) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0, 'position': 'unknown'}
        
        closes_arr = np.array(closes)
        
        # Calculate SMA
        sma = np.mean(closes_arr[-period:])
        
        # Calculate standard deviation
        std = np.std(closes_arr[-period:])
        
        # Calculate bands
        upper = sma + (std_dev * std)
        lower = sma - (std_dev * std)
        
        # Determine position
        current_price = closes[-1]
        if current_price > upper:
            position = 'above_upper'
        elif current_price < lower:
            position = 'below_lower'
        elif current_price > sma:
            position = 'upper_half'
        else:
            position = 'lower_half'
        
        return {
            'upper': round(upper, 2),
            'middle': round(sma, 2),
            'lower': round(lower, 2),
            'position': position,
            'bandwidth': round((upper - lower) / sma * 100, 2)
        }
    
    @staticmethod
    def _ema(data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average."""
        ema = np.zeros_like(data)
        multiplier = 2 / (period + 1)
        
        # First EMA is SMA
        ema[period - 1] = np.mean(data[:period])
        
        # Calculate EMA
        for i in range(period, len(data)):
            ema[i] = (data[i] - ema[i - 1]) * multiplier + ema[i - 1]
        
        return ema


def analyze_technical_signals(closes: List[float], highs: List[float], 
                               lows: List[float]) -> Dict[str, Any]:
    """Analyze all technical indicators and generate signals.
    
    Args:
        closes: List of closing prices
        highs: List of high prices
        lows: List of low prices
        
    Returns:
        Dictionary with all technical indicators and combined signal
    """
    ti = TechnicalIndicators()
    
    macd = ti.calculate_macd(closes)
    rsi = ti.calculate_rsi(closes)
    kdj = ti.calculate_kdj(highs, lows, closes)
    boll = ti.calculate_bollinger(closes)
    
    # Generate combined signal
    signals = []
    
    if macd['trend'] == 'bullish':
        signals.append(('MACD', 'bullish', 1))
    elif macd['trend'] == 'bearish':
        signals.append(('MACD', 'bearish', -1))
    
    if rsi['interpretation'] == 'oversold':
        signals.append(('RSI', 'oversold', 1))
    elif rsi['interpretation'] == 'overbought':
        signals.append(('RSI', 'overbought', -1))
    
    if kdj['signal'] == 'oversold':
        signals.append(('KDJ', 'oversold', 1))
    elif kdj['signal'] == 'overbought':
        signals.append(('KDJ', 'overbought', -1))
    
    if boll['position'] == 'below_lower':
        signals.append(('BOLL', 'below_lower', 1))
    elif boll['position'] == 'above_upper':
        signals.append(('BOLL', 'above_upper', -1))
    
    # Calculate combined score
    total_score = sum(s[2] for s in signals)
    
    if total_score >= 2:
        combined_signal = 'strong_buy'
    elif total_score == 1:
        combined_signal = 'buy'
    elif total_score <= -2:
        combined_signal = 'strong_sell'
    elif total_score == -1:
        combined_signal = 'sell'
    else:
        combined_signal = 'neutral'
    
    return {
        'macd': macd,
        'rsi': rsi,
        'kdj': kdj,
        'bollinger': boll,
        'signals': signals,
        'combined_signal': combined_signal,
        'score': total_score
    }
