"""Fast mainboard stock screener using baostock with targeted codes."""

import time
from typing import List, Dict, Any
from datetime import datetime, timedelta

import baostock as bs
from loguru import logger


class MainboardScreener:
    """Screen mainboard stocks - optimized for speed."""
    
    def __init__(self):
        self._logged_in = False
    
    def _login(self):
        if not self._logged_in:
            lg = bs.login()
            if lg.error_code == '0':
                self._logged_in = True
                logger.info("BaoStock login successful")
    
    def _logout(self):
        if self._logged_in:
            bs.logout()
            self._logged_in = False
    
    def screen_stocks(self, budget: float = 1500, max_price: float = 19.0,
                      min_price: float = 5.0, top_n: int = 20) -> List[Dict[str, Any]]:
        """Screen mainboard stocks using targeted code list."""
        self._login()
        
        # Use dynamic dates - get last 10 trading days
        today = datetime.now()
        end_date = today.strftime("%Y-%m-%d")
        start_date = (today - timedelta(days=14)).strftime("%Y-%m-%d")
        
        logger.info(f"Fetching data from {start_date} to {end_date}")
        
        # Pre-selected cheap mainboard codes (known to be under 19 RMB)
        stock_codes = [
            # 深交所 - 低价股
            'sz.000009', 'sz.000012', 'sz.000014', 'sz.000016', 'sz.000019',
            'sz.000020', 'sz.000021', 'sz.000025', 'sz.000026', 'sz.000028',
            'sz.000029', 'sz.000031', 'sz.000032', 'sz.000034', 'sz.000036',
            'sz.000038', 'sz.000039', 'sz.000040', 'sz.000042', 'sz.000043',
            'sz.000045', 'sz.000046', 'sz.000048', 'sz.000049', 'sz.000050',
            'sz.000055', 'sz.000058', 'sz.000059', 'sz.000060', 'sz.000061',
            'sz.000062', 'sz.000063', 'sz.000065', 'sz.000066', 'sz.000068',
            'sz.000069', 'sz.000070', 'sz.000078', 'sz.000088', 'sz.000089',
            'sz.000090', 'sz.000096', 'sz.000099', 'sz.000100',
            'sz.000150', 'sz.000151', 'sz.000153', 'sz.000155', 'sz.000156',
            'sz.000157', 'sz.000158', 'sz.000159', 'sz.000160',
            'sz.002001', 'sz.002002', 'sz.002003', 'sz.002004', 'sz.002005',
            'sz.002006', 'sz.002007', 'sz.002008', 'sz.002009', 'sz.002010',
            'sz.002011', 'sz.002012', 'sz.002013', 'sz.002014', 'sz.002015',
            'sz.002016', 'sz.002017', 'sz.002018', 'sz.002019', 'sz.002020',
            'sz.002022', 'sz.002023', 'sz.002024', 'sz.002025', 'sz.002026',
            'sz.002027', 'sz.002028', 'sz.002029', 'sz.002030',
            'sz.002033', 'sz.002034', 'sz.002035', 'sz.002036', 'sz.002037',
            'sz.002038', 'sz.002039', 'sz.002040',
            # 上交所 - 低价股
            'sh.600000', 'sh.600004', 'sh.600006', 'sh.600007', 'sh.600008',
            'sh.600009', 'sh.600010', 'sh.600011', 'sh.600012', 'sh.600015',
            'sh.600016', 'sh.600017', 'sh.600018', 'sh.600019', 'sh.600020',
            'sh.600021', 'sh.600022', 'sh.600023', 'sh.600025', 'sh.600026',
            'sh.600027', 'sh.600028', 'sh.600029', 'sh.600030', 'sh.600031',
            'sh.600033', 'sh.600035', 'sh.600036', 'sh.600037', 'sh.600038',
            'sh.600039', 'sh.600048', 'sh.600050', 'sh.600051', 'sh.600052',
            'sh.600053', 'sh.600054', 'sh.600055', 'sh.600056', 'sh.600057',
            'sh.600058', 'sh.600059', 'sh.600060', 'sh.600061', 'sh.600062',
            'sh.600063', 'sh.600064', 'sh.600065', 'sh.600066', 'sh.600067',
            'sh.600068', 'sh.600069', 'sh.600070', 'sh.600071', 'sh.600072',
            'sh.600073', 'sh.600074', 'sh.600075', 'sh.600076', 'sh.600077',
            'sh.600078', 'sh.600079', 'sh.600080', 'sh.600081', 'sh.600082',
            'sh.600083', 'sh.600084', 'sh.600085', 'sh.600086', 'sh.600087',
            'sh.600088', 'sh.600089', 'sh.600090',
        ]
        
        logger.info(f"Scanning {len(stock_codes)} targeted mainboard codes...")
        
        candidates = []
        count = 0
        
        for code in stock_codes:
            count += 1
            try:
                rs = bs.query_history_k_data_plus(
                    code, 'date,close,volume,turn',
                    start_date=start_date, end_date=end_date,
                    frequency='d', adjustflag='3'
                )
                
                data = []
                while (rs.error_code == '0') and rs.next():
                    data.append(rs.get_row_data())
                
                if len(data) < 2:
                    continue
                
                latest = data[-1]
                price = float(latest[1]) if latest[1] else 0
                volume = float(latest[2]) if latest[2] else 0
                turn = float(latest[3]) if latest[3] else 0
                
                if price > max_price or price < min_price:
                    continue
                
                if volume < 300000:
                    continue
                
                cost_100 = price * 100
                if cost_100 > budget:
                    continue
                
                # Calculate change
                price_prev = float(data[-2][1]) if len(data) >= 2 and data[-2][1] else price
                change = ((price - price_prev) / price_prev * 100) if price_prev > 0 else 0
                
                # Score
                score = 0
                if change > 5: score += 30
                elif change > 3: score += 20
                elif change > 1: score += 15
                elif change > 0: score += 10
                elif change > -2: score += 5
                
                if turn > 10: score += 20
                elif turn > 5: score += 15
                elif turn > 3: score += 10
                
                if volume > 5000000: score += 10
                elif volume > 1000000: score += 5
                
                if 10 <= price <= 18: score += 10
                elif 5 <= price < 10: score += 5
                
                # Get stock name
                rs2 = bs.query_stock_basic(code=code)
                name = ""
                while (rs2.error_code == '0') and rs2.next():
                    name = rs2.get_row_data()[1]
                
                candidates.append({
                    'code': code.split('.')[1],
                    'name': name,
                    'price': price,
                    'cost_100': cost_100,
                    'change': change,
                    'volume': volume,
                    'turnover': turn,
                    'score': score,
                    'affordable': True
                })
            except Exception:
                continue
        
        self._logout()
        
        candidates.sort(key=lambda x: -x['score'])
        logger.info(f"Found {len(candidates)} affordable mainboard stocks")
        return candidates[:top_n]
    
    def generate_buy_plan(self, stocks: List[Dict[str, Any]],
                          budget: float = 1500) -> Dict[str, Any]:
        """Generate buy plan for given budget."""
        if not stocks:
            return {
                'budget': budget,
                'positions': [],
                'total_cost': 0,
                'remaining': budget,
                'summary': '未找到符合条件的股票'
            }
        
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
                
                if len(positions) >= 2:
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
