"""Fast mainboard stock screener using akshare batch API."""

import time
from typing import List, Dict, Any
from datetime import datetime

from loguru import logger


class MainboardScreener:
    """Screen mainboard stocks - optimized for speed."""
    
    def screen_stocks(self, budget: float = 1900, max_price: float = 19.0, 
                      min_price: float = 5.0, top_n: int = 15) -> List[Dict[str, Any]]:
        """Screen mainboard stocks using akshare batch API."""
        try:
            import akshare as ak
            
            logger.info("Fetching A-share stock list via akshare...")
            
            # Get all A-share stocks in one call
            df = ak.stock_zh_a_spot_em()
            
            if df.empty:
                logger.warning("No stock data returned")
                return []
            
            logger.info(f"Got {len(df)} stocks, filtering...")
            
            candidates = []
            
            for _, row in df.iterrows():
                try:
                    code = str(row.get("代码", ""))
                    name = str(row.get("名称", ""))
                    price = float(row.get("最新价", 0))
                    change = float(row.get("涨跌幅", 0))
                    volume = float(row.get("成交量", 0))
                    amount = float(row.get("成交额", 0))
                    turnover = float(row.get("换手率", 0))
                    pe = row.get("市盈率-动态", None)
                    pb = row.get("市净率", None)
                    
                    # Filter: mainboard only (000xxx, 001xxx, 002xxx, 600xxx, 601xxx, 603xxx, 605xxx)
                    if not (code.startswith(('000', '001', '002', '600', '601', '603', '605'))):
                        continue
                    
                    # Filter: price range
                    if price > max_price or price < min_price:
                        continue
                    
                    # Filter: minimum volume
                    if volume < 500000:
                        continue
                    
                    # Calculate cost for 100 shares
                    cost_100 = price * 100
                    
                    # Skip if over budget
                    if cost_100 > budget:
                        continue
                    
                    # Score based on momentum (today's change as proxy)
                    score = 0
                    
                    # Momentum score
                    if change > 5: score += 30
                    elif change > 3: score += 20
                    elif change > 1: score += 15
                    elif change > 0: score += 10
                    elif change > -2: score += 5
                    
                    # Turnover score (high = active)
                    if turnover > 10: score += 20
                    elif turnover > 5: score += 15
                    elif turnover > 3: score += 10
                    elif turnover > 1: score += 5
                    
                    # Volume score
                    if volume > 10000000: score += 10
                    elif volume > 5000000: score += 5
                    
                    # Price sweet spot
                    if 10 <= price <= 18: score += 10
                    elif 5 <= price < 10: score += 5
                    
                    # PE filter (avoid negative/very high PE)
                    if pe and isinstance(pe, (int, float)):
                        if 0 < pe < 100: score += 5
                        elif pe > 200: score -= 5
                    
                    candidates.append({
                        'code': code,
                        'name': name,
                        'price': price,
                        'cost_100': cost_100,
                        'change': change,
                        'volume': volume,
                        'turnover': turnover,
                        'pe': pe,
                        'pb': pb,
                        'score': score,
                        'affordable': True
                    })
                except Exception:
                    continue
            
            # Sort by score
            candidates.sort(key=lambda x: -x['score'])
            
            logger.info(f"Found {len(candidates)} affordable mainboard stocks")
            return candidates[:top_n]
            
        except Exception as e:
            logger.error(f"Screener failed: {e}")
            return []
    
    def generate_buy_plan(self, stocks: List[Dict[str, Any]], 
                          budget: float = 1900) -> Dict[str, Any]:
        """Generate buy plan for given budget."""
        if not stocks:
            return {
                'budget': budget,
                'positions': [],
                'total_cost': 0,
                'remaining': budget,
                'summary': '未找到符合条件的股票'
            }
        
        # Filter affordable and sort by score
        affordable = [s for s in stocks if s['affordable']]
        affordable.sort(key=lambda x: -x['score'])
        
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
                    'change': stock['change'],
                    'score': stock['score']
                })
                remaining -= stock['cost_100']
                
                if len(positions) >= 2:  # Max 2 positions
                    break
        
        total_cost = sum(p['cost'] for p in positions)
        
        if positions:
            pos_desc = " + ".join([f"{p['name']}({p['cost']}元)" for p in positions])
            summary = f"建议买入: {pos_desc}，总计{total_cost}元，剩余{remaining}元"
        else:
            summary = "当前预算不足或无合适标的"
        
        return {
            'budget': budget,
            'positions': positions,
            'total_cost': total_cost,
            'remaining': round(remaining, 2),
            'summary': summary
        }
