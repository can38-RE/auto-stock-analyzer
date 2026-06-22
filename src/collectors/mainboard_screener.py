"""Mainboard stock screener for aggressive small-capital strategy."""

import time
from typing import List, Dict, Any
from datetime import datetime

import baostock as bs
from loguru import logger


class MainboardScreener:
    """Screen mainboard stocks for aggressive small-capital strategy."""
    
    def __init__(self):
        """Initialize screener."""
        self._logged_in = False
    
    def _login(self):
        """Login to baostock."""
        if not self._logged_in:
            try:
                lg = bs.login()
                if lg.error_code == '0':
                    self._logged_in = True
                    logger.info("BaoStock login successful")
                else:
                    logger.error(f"BaoStock login failed: {lg.error_msg}")
            except Exception as e:
                logger.error(f"BaoStock login error: {e}")
    
    def _logout(self):
        """Logout from baostock."""
        if self._logged_in:
            bs.logout()
            self._logged_in = False
    
    def screen_stocks(self, budget: float = 1900, max_price: float = 19.0, 
                      min_price: float = 5.0, top_n: int = 15) -> List[Dict[str, Any]]:
        """Screen mainboard stocks based on aggressive criteria.
        
        Args:
            budget: Total budget in RMB
            max_price: Maximum stock price per share
            min_price: Minimum stock price per share
            top_n: Number of top stocks to return
            
        Returns:
            List of stock dictionaries with scores
        """
        self._login()
        
        # Generate mainboard stock codes
        stock_codes = []
        
        # 深交所主板: 000xxx, 001xxx, 002xxx
        for i in range(0, 400):
            stock_codes.append(f"sz.{i:06d}")
        for i in range(1000, 1200):
            stock_codes.append(f"sz.{i:06d}")
        for i in range(2000, 2300):
            stock_codes.append(f"sz.{i:06d}")
        
        # 上交所主板: 600xxx, 601xxx, 603xxx, 605xxx
        for i in range(600000, 600400):
            stock_codes.append(f"sh.{i}")
        for i in range(601000, 601300):
            stock_codes.append(f"sh.{i}")
        for i in range(603000, 603400):
            stock_codes.append(f"sh.{i}")
        for i in range(605000, 605100):
            stock_codes.append(f"sh.{i}")
        
        logger.info(f"Scanning {len(stock_codes)} mainboard codes...")
        
        candidates = []
        count = 0
        
        for code in stock_codes:
            count += 1
            if count % 1000 == 0:
                logger.info(f"Scanned {count} codes...")
            
            try:
                stock = self._analyze_stock(code, min_price, max_price, budget)
                if stock and stock['score'] >= 25:
                    candidates.append(stock)
            except Exception:
                pass
        
        self._logout()
        
        # Sort by score
        candidates.sort(key=lambda x: -x['score'])
        
        logger.info(f"Found {len(candidates)} qualifying stocks")
        return candidates[:top_n]
    
    def _analyze_stock(self, code: str, min_price: float, max_price: float, 
                       budget: float) -> Dict[str, Any] | None:
        """Analyze a single stock with T+1 rule consideration.
        
        T+1 Rule: Can only sell the day AFTER buying.
        Strategy: Look for stocks with multi-day momentum, not just single-day spikes.
        """
        rs = bs.query_history_k_data_plus(
            code, 'date,close,volume,turn',
            start_date='2026-06-10', end_date='2026-06-22',
            frequency='d', adjustflag='3'
        )
        
        data = []
        while (rs.error_code == '0') and rs.next():
            data.append(rs.get_row_data())
        
        if len(data) < 5:  # Need at least 5 days of data
            return None
        
        latest = data[-1]
        price = float(latest[1]) if latest[1] else 0
        volume = float(latest[2]) if latest[2] else 0
        turn = float(latest[3]) if latest[3] else 0
        
        # Filter price range
        if price > max_price or price < min_price:
            return None
        
        # Filter volume
        if volume < 500000:
            return None
        
        # Calculate multi-day momentum (T+1 safe)
        prices = [float(d[1]) for d in data if d[1]]
        if len(prices) < 5:
            return None
        
        # 3-day momentum (more reliable than 1-day)
        momentum_3d = ((prices[-1] - prices[-4]) / prices[-4] * 100) if prices[-4] > 0 else 0
        
        # 5-day momentum
        momentum_5d = ((prices[-1] - prices[-6]) / prices[-6] * 100) if len(prices) >= 6 and prices[-6] > 0 else 0
        
        # Check if stock is in uptrend (higher lows)
        recent_lows = [float(data[i][3]) for i in range(-5, 0) if data[i][3]]
        uptrend = len(recent_lows) >= 3 and recent_lows[-1] > recent_lows[-3]
        
        # Check limit up in last 3 days (not just today)
        has_limit_recent = False
        for j in range(max(1, len(data)-3), len(data)):
            prev = float(data[j-1][1]) if data[j-1][1] else 0
            curr = float(data[j][1]) if data[j][1] else 0
            if prev > 0 and ((curr - prev) / prev * 100) >= 9.5:
                has_limit_recent = True
        
        # Volume increase (sign of continued interest)
        vol_recent = [float(data[i][2]) for i in range(-3, 0) if data[i][2]]
        vol_avg = sum(vol_recent) / len(vol_recent) if vol_recent else 0
        vol_earlier = [float(data[i][2]) for i in range(-6, -3) if data[i][2]]
        vol_avg_earlier = sum(vol_earlier) / len(vol_earlier) if vol_earlier else 1
        volume_increase = (vol_recent[-1] / vol_avg_earlier) if vol_avg_earlier > 0 else 1
        
        # Score calculation (T+1 optimized)
        score = 0
        
        # Multi-day momentum (more important for T+1)
        if momentum_3d > 15: score += 35
        elif momentum_3d > 10: score += 25
        elif momentum_3d > 5: score += 15
        elif momentum_3d > 0: score += 5
        
        # 5-day trend
        if momentum_5d > 20: score += 15
        elif momentum_5d > 10: score += 10
        
        # Uptrend (higher lows)
        if uptrend: score += 15
        
        # Recent limit up
        if has_limit_recent: score += 20
        
        # Volume increase (continued buying interest)
        if volume_increase > 1.5: score += 10
        elif volume_increase > 1.2: score += 5
        
        # High turnover (active trading)
        if turn > 10: score += 10
        elif turn > 5: score += 5
        
        # Price sweet spot
        if 10 <= price <= 18: score += 10
        elif 5 <= price < 10: score += 5
        
        cost_100 = price * 100
        
        # Get stock name
        rs2 = bs.query_stock_basic(code=code)
        name = ""
        while (rs2.error_code == '0') and rs2.next():
            name = rs2.get_row_data()[1]
        
        return {
            'code': code.split('.')[1],
            'name': name,
            'price': price,
            'cost_100': cost_100,
            'momentum_3d': momentum_3d,
            'momentum_5d': momentum_5d,
            'turnover': turn,
            'has_limit_recent': has_limit_recent,
            'uptrend': uptrend,
            'volume_increase': volume_increase,
            'score': score,
            'affordable': cost_100 <= budget,
            't1_safe': momentum_3d > 0 and uptrend  # T+1 safe indicator
        }
    
    def generate_buy_plan(self, stocks: List[Dict[str, Any]], 
                          budget: float = 1900) -> Dict[str, Any]:
        """Generate buy plan for given budget.
        
        Args:
            stocks: List of screened stocks
            budget: Total budget in RMB
            
        Returns:
            Buy plan dictionary
        """
        # Filter affordable stocks
        affordable = [s for s in stocks if s['affordable']]
        
        if not affordable:
            return {
                'budget': budget,
                'positions': [],
                'total_cost': 0,
                'remaining': budget,
                'summary': '未找到符合条件的股票'
            }
        
        # Try to buy top stocks
        positions = []
        remaining = budget
        
        for stock in affordable:
            if stock['cost_100'] <= remaining:
                positions.append({
                    'code': stock['code'],
                    'name': stock['name'],
                    'price': stock['price'],
                    'shares': 100,
                    'cost': stock['cost_100'],
                    'momentum': stock['momentum'],
                    'score': stock['score']
                })
                remaining -= stock['cost_100']
                
                if len(positions) >= 2:  # Max 2 positions
                    break
        
        total_cost = sum(p['cost'] for p in positions)
        
        # Generate summary
        if positions:
            pos_desc = " + ".join([f"{p['name']}({p['cost']}元)" for p in positions])
            summary = f"建议买入: {pos_desc}，总计{total_cost}元，剩余{remaining}元"
        else:
            summary = "当前预算不足，建议等待资金"
        
        return {
            'budget': budget,
            'positions': positions,
            'total_cost': total_cost,
            'remaining': round(remaining, 2),
            'summary': summary
        }


def format_screener_results(stocks: List[Dict[str, Any]], 
                           buy_plan: Dict[str, Any]) -> str:
    """Format screener results as readable text."""
    lines = [
        "=" * 60,
        "📊 主板股票筛选结果",
        "=" * 60,
        "",
        f"预算: {buy_plan['budget']}元",
        f"筛选条件: 主板 | 价格5-19元 | 高动量",
        "",
        "候选股票:",
        f"{'代码':<10} {'名称':<15} {'价格':>8} {'1手':>10} {'动量':>10} {'评分':>6}",
        "-" * 65,
    ]
    
    for s in stocks[:10]:
        lines.append(f"{s['code']:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost_100']:>10.0f} {s['momentum']:>+9.2f}% {s['score']:>6}")
    
    lines.extend([
        "",
        "=" * 60,
        "💰 买入方案",
        "=" * 60,
        "",
    ])
    
    if buy_plan['positions']:
        for i, pos in enumerate(buy_plan['positions'], 1):
            lines.append(f"第{i}手: {pos['code']} {pos['name']}")
            lines.append(f"  价格: {pos['price']:.2f}元 × 100股 = {pos['cost']}元")
            lines.append(f"  动量: {pos['momentum']:+.2f}% | 评分: {pos['score']}")
            lines.append("")
        
        lines.append(f"总投入: {buy_plan['total_cost']}元")
        lines.append(f"剩余资金: {buy_plan['remaining']}元")
    else:
        lines.append("暂无合适标的")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)
