"""Stock trend analyzer with entry price strategies.

Analyzes recent price trends and provides:
1. Current trend status (uptrend/downtrend/consolidation)
2. Optimal entry prices
3. Different strategies based on trend patterns
"""

import baostock as bs
from typing import List, Dict, Any, Tuple
from loguru import logger


class TrendAnalyzer:
    """Analyze stock trends and provide entry strategies."""
    
    def __init__(self):
        self._logged_in = False
    
    def _login(self):
        if not self._logged_in:
            bs.login()
            self._logged_in = True
    
    def _logout(self):
        if self._logged_in:
            bs.logout()
            self._logged_in = False
    
    def analyze_stock(self, code: str, name: str = "") -> Dict[str, Any]:
        """Full trend analysis for a stock."""
        self._login()
        
        if code.startswith('6'):
            bs_code = f'sh.{code}'
        else:
            bs_code = f'sz.{code}'
        
        # Get 20 days of data
        rs = bs.query_history_k_data_plus(
            bs_code,
            'date,open,high,low,close,volume',
            start_date='2026-05-20',
            end_date='2026-06-23',
            frequency='d',
            adjustflag='3'
        )
        
        data = []
        while (rs.error_code == '0') and rs.next():
            data.append(rs.get_row_data())
        
        if len(data) < 10:
            return None
        
        # Parse data
        prices = []
        for d in data:
            prices.append({
                'date': d[0],
                'open': float(d[1]) if d[1] else 0,
                'high': float(d[2]) if d[2] else 0,
                'low': float(d[3]) if d[3] else 0,
                'close': float(d[4]) if d[4] else 0,
                'volume': float(d[5]) if d[5] else 0,
            })
        
        latest = prices[-1]
        current_price = latest['close']
        
        # Calculate key metrics
        trend = self._identify_trend(prices)
        support_resistance = self._calculate_support_resistance(prices)
        entry_prices = self._calculate_entry_prices(prices, current_price)
        strategy = self._generate_strategy(prices, trend, current_price)
        
        return {
            'code': code,
            'name': name,
            'current_price': current_price,
            'today_change': self._calculate_change(prices[-2]['close'], current_price) if len(prices) >= 2 else 0,
            'trend': trend,
            'support_resistance': support_resistance,
            'entry_prices': entry_prices,
            'strategy': strategy,
            'recent_prices': prices[-5:],  # Last 5 days
        }
    
    def _identify_trend(self, prices: List[Dict]) -> Dict[str, Any]:
        """Identify current trend."""
        if len(prices) < 10:
            return {'direction': 'unknown', 'strength': 0, 'description': '数据不足'}
        
        # Calculate moving averages
        closes = [p['close'] for p in prices]
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10
        ma20 = sum(closes) / len(closes)
        
        current = closes[-1]
        
        # Determine trend
        if current > ma5 > ma10 > ma20:
            direction = 'strong_uptrend'
            strength = 90
            desc = '强势上涨（均线多头排列）'
        elif current > ma5 > ma10:
            direction = 'uptrend'
            strength = 70
            desc = '上涨趋势'
        elif current > ma5:
            direction = 'weak_uptrend'
            strength = 55
            desc = '弱上涨'
        elif current < ma5 < ma10 < ma20:
            direction = 'strong_downtrend'
            strength = 10
            desc = '强势下跌（均线空头排列）'
        elif current < ma5 < ma10:
            direction = 'downtrend'
            strength = 30
            desc = '下跌趋势'
        elif current < ma5:
            direction = 'weak_downtrend'
            strength = 45
            desc = '弱下跌'
        else:
            direction = 'consolidation'
            strength = 50
            desc = '震荡整理'
        
        return {
            'direction': direction,
            'strength': strength,
            'description': desc,
            'ma5': round(ma5, 2),
            'ma10': round(ma10, 2),
            'ma20': round(ma20, 2),
        }
    
    def _calculate_support_resistance(self, prices: List[Dict]) -> Dict[str, float]:
        """Calculate support and resistance levels."""
        recent = prices[-10:]
        
        highs = [p['high'] for p in recent]
        lows = [p['low'] for p in recent]
        closes = [p['close'] for p in recent]
        
        # Simple support/resistance
        resistance = max(highs)
        support = min(lows)
        
        # Pivot point
        pivot = (resistance + support + closes[-1]) / 3
        
        return {
            'resistance': round(resistance, 2),
            'support': round(support, 2),
            'pivot': round(pivot, 2),
            'range': round(resistance - support, 2),
            'range_pct': round((resistance - support) / support * 100, 2),
        }
    
    def _calculate_entry_prices(self, prices: List[Dict], current: float) -> Dict[str, float]:
        """Calculate optimal entry prices."""
        sr = self._calculate_support_resistance(prices)
        
        # Different entry levels
        return {
            'aggressive': round(current * 0.99, 2),      # 激进入场：当前价-1%
            'moderate': round(current * 0.97, 2),         # 稳健入场：当前价-3%
            'conservative': round(sr['support'], 2),      # 保守入场：支撑位
            'breakout': round(sr['resistance'] * 1.01, 2), # 突破入场：阻力位+1%
            'stop_loss': round(current * 0.93, 2),        # 止损位：当前价-7%
            'take_profit_1': round(current * 1.10, 2),    # 止盈1：+10%
            'take_profit_2': round(current * 1.20, 2),    # 止盈2：+20%
        }
    
    def _generate_strategy(self, prices: List[Dict], trend: Dict, current: float) -> Dict[str, Any]:
        """Generate entry strategy based on trend."""
        direction = trend['direction']
        sr = self._calculate_support_resistance(prices)
        entry = self._calculate_entry_prices(prices, current)
        
        if direction in ['strong_uptrend', 'uptrend']:
            return {
                'type': '追涨策略',
                'emoji': '🔥',
                'action': '立即买入或回调买入',
                'entry_price': entry['aggressive'],
                'reason': '趋势向上，可追涨',
                'risk_level': '中等',
                'tips': [
                    '可在当前价位直接买入',
                    '若回调到5日均线附近加仓',
                    f'止损位: {entry["stop_loss"]}元 (-7%)',
                    f'第一止盈: {entry["take_profit_1"]}元 (+10%)',
                    '注意：T+1规则，今天买明天才能卖',
                ]
            }
        
        elif direction in ['weak_uptrend']:
            return {
                'type': '回调买入策略',
                emoji: '📉',
                'action': '等待回调后买入',
                'entry_price': entry['moderate'],
                'reason': '上涨力度减弱，等回调',
                'risk_level': '较低',
                'tips': [
                    f'等待价格回调到{entry["moderate"]}元附近',
                    f'支撑位: {sr["support"]}元',
                    '确认支撑有效后再买入',
                    f'止损位: {entry["stop_loss"]}元',
                    'T+1规则：买入后次日才能卖出',
                ]
            }
        
        elif direction in ['consolidation']:
            return {
                'type': '区间交易策略',
                'emoji': '↔️',
                'action': '支撑位买入，阻力位卖出',
                'entry_price': sr['support'],
                'reason': '震荡区间，高抛低吸',
                'risk_level': '中等',
                'tips': [
                    f'在支撑位{sr["support"]}元附近买入',
                    f'在阻力位{sr["resistance"]}元附近卖出',
                    f'区间波动: {sr["range_pct"]}%',
                    '严格止损，不要死扛',
                    'T+1规则：当天买入次日才能卖出',
                ]
            }
        
        elif direction in ['weak_downtrend']:
            return {
                'type': '观望策略',
                'emoji': '⏳',
                'action': '观望为主，等待企稳',
                'entry_price': entry['conservative'],
                'reason': '下跌趋势，不宜追跌',
                'risk_level': '较高',
                'tips': [
                    '建议观望，等待趋势反转',
                    f'若跌破支撑位{sr["support"]}元，止损',
                    '等待放量阳线确认反转',
                    '不要抄底，等右侧信号',
                    'T+1规则：风险更大',
                ]
            }
        
        else:  # downtrend or strong_downtrend
            return {
                'type': '回避策略',
                'emoji': '🚫',
                'action': '回避，不建议买入',
                'entry_price': 0,
                'reason': '下跌趋势，风险太大',
                'risk_level': '高',
                'tips': [
                    '当前处于下跌趋势，不建议买入',
                    '等待趋势完全反转再考虑',
                    '关注成交量变化',
                    '宁可错过，不要做错',
                ]
            }
    
    def _calculate_change(self, prev: float, current: float) -> float:
        """Calculate percentage change."""
        if prev > 0:
            return round((current - prev) / prev * 100, 2)
        return 0
    
    def analyze_multiple(self, stocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple stocks."""
        results = []
        
        for stock in stocks:
            try:
                analysis = self.analyze_stock(stock['code'], stock.get('name', ''))
                if analysis:
                    # Merge with original stock data
                    analysis.update(stock)
                    results.append(analysis)
            except Exception as e:
                logger.warning(f"Failed to analyze {stock['code']}: {e}")
        
        self._logout()
        return results


def format_trend_analysis(analysis: Dict[str, Any]) -> str:
    """Format trend analysis as readable text."""
    lines = [
        "=" * 60,
        f"📊 {analysis['name']}({analysis['code']}) 走势分析",
        "=" * 60,
        "",
        f"当前价格: {analysis['current_price']}元",
        f"今日涨跌: {analysis['today_change']:+.2f}%",
        "",
        f"趋势判断: {analysis['trend']['emoji']} {analysis['trend']['description']}",
        f"  MA5: {analysis['trend']['ma5']}元",
        f"  MA10: {analysis['trend']['ma10']}元",
        f"  MA20: {analysis['trend']['ma20']}元",
        "",
        "支撑阻力:",
        f"  阻力位: {analysis['support_resistance']['resistance']}元",
        f"  支撑位: {analysis['support_resistance']['support']}元",
        f"  波动区间: {analysis['support_resistance']['range_pct']}%",
        "",
        f"入场策略: {analysis['strategy']['type']}",
        f"建议动作: {analysis['strategy']['action']}",
        f"建议入场价: {analysis['strategy']['entry_price']}元",
        f"风险等级: {analysis['strategy']['risk_level']}",
        "",
        "操作建议:",
    ]
    
    for tip in analysis['strategy']['tips']:
        lines.append(f"  • {tip}")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
