"""Real-time stock analysis for today's trading decision."""

import baostock as bs
import requests
from datetime import datetime, timedelta

def get_realtime_price(code):
    """Get real-time price using Sina Finance API. Code must be in format sh.600000 or sz.000001."""
    try:
        # Convert baostock format to Sina format: sh.600000 -> sh600000
        symbol = code.replace('.', '')
        
        url = f"https://hq.sinajs.cn/list={symbol}"
        response = requests.get(url, headers={'Referer': 'https://finance.sina.com.cn'}, timeout=5)
        
        if response.status_code == 200:
            data = response.text.split('"')[1].split(',')
            if len(data) > 3:
                return {
                    'price': float(data[3]),
                    'change': float(data[3]) - float(data[2]) if data[2] else 0,
                    'change_pct': ((float(data[3]) - float(data[2])) / float(data[2]) * 100) if data[2] else 0,
                    'volume': float(data[8]) if len(data) > 8 else 0,
                    'high': float(data[4]) if data[4] else 0,
                    'low': float(data[5]) if data[5] else 0,
                }
    except:
        pass
    return None

def get_historical_data(code, days=10):
    """Get historical data using baostock."""
    try:
        bs.login()
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        rs = bs.query_history_k_data_plus(
            code, 'date,close,volume,turn',
            start_date=start_date, end_date=end_date,
            frequency='d', adjustflag='3'
        )
        
        data = []
        while (rs.error_code == '0') and rs.next():
            data.append(rs.get_row_data())
        
        bs.logout()
        
        if data:
            closes = [float(d[1]) for d in data if d[1]]
            volumes = [float(d[2]) for d in data if d[2]]
            
            return {
                'closes': closes,
                'volumes': volumes,
                'turnover': float(data[-1][3]) if data[-1][3] else 0,
                'avg_volume': sum(volumes) / len(volumes) if volumes else 0,
            }
    except:
        pass
    return None

def analyze_stock(code, name):
    """Comprehensive analysis of a stock."""
    
    # Get historical data
    hist = get_historical_data(code, days=10)
    if not hist or len(hist['closes']) < 3:
        return None
    
    # Calculate metrics
    closes = hist['closes']
    change_1d = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) >= 2 else 0
    change_3d = ((closes[-1] - closes[-4]) / closes[-4] * 100) if len(closes) >= 4 else 0
    change_5d = ((closes[-1] - closes[-6]) / closes[-6] * 100) if len(closes) >= 6 else 0
    
    # Current price
    current_price = closes[-1]
    cost_100 = current_price * 100
    
    # Check if affordable
    if cost_100 > 1500 or current_price < 3:
        return None
    
    # Score calculation (ultra-short-term focus)
    score = 0
    
    # Momentum score (higher weight for short-term)
    if change_1d > 5: score += 35
    elif change_1d > 3: score += 25
    elif change_1d > 1: score += 15
    elif change_1d > 0: score += 10
    
    # 3-day momentum
    if change_3d > 10: score += 25
    elif change_3d > 5: score += 15
    elif change_3d > 0: score += 10
    
    # 5-day momentum
    if change_5d > 15: score += 20
    elif change_5d > 8: score += 15
    elif change_5d > 0: score += 10
    
    # Volume factor
    if hist['turnover'] > 10: score += 15
    elif hist['turnover'] > 5: score += 10
    elif hist['turnover'] > 3: score += 5
    
    # Price sweet spot (10-15 RMB)
    if 10 <= current_price <= 15: score += 10
    elif 5 <= current_price < 10: score += 5
    
    return {
        'code': code,
        'name': name,
        'price': current_price,
        'cost_100': cost_100,
        'change_1d': round(change_1d, 2),
        'change_3d': round(change_3d, 2),
        'change_5d': round(change_5d, 2),
        'turnover': hist['turnover'],
        'score': score
    }

# Main analysis
print("=" * 70)
print(f"超短线选股分析 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("策略: 超短线 | 预算: 1500元 | 目标: 明天赚100+元")
print("=" * 70)

# Mainboard stock codes
stock_codes = [
    'sz.000100', 'sz.002020', 'sz.600063', 'sz.600076', 'sz.000012',
    'sz.000059', 'sz.000068', 'sz.002023', 'sz.600075', 'sz.002014',
    'sz.002030', 'sz.600073', 'sz.600080', 'sz.000061', 'sz.000089',
    'sz.000060', 'sz.000050', 'sz.600058', 'sz.000066', 'sz.000025',
]

# Get stock names
bs.login()
stock_names = {}
for code in stock_codes:
    rs = bs.query_stock_basic(code=code)
    while (rs.error_code == '0') and rs.next():
        stock_names[code] = rs.get_row_data()[1]
bs.logout()

print(f"\n分析 {len(stock_codes)} 只主板股票...")

candidates = []
for code in stock_codes:
    name = stock_names.get(code, "")
    result = analyze_stock(code, name)
    if result:
        candidates.append(result)

# Sort by score
candidates.sort(key=lambda x: -x['score'])

print(f"\n{'排名':<4} {'代码':<10} {'名称':<15} {'价格':>8} {'1手成本':>10} {'今日':>8} {'3日':>8} {'5日':>8} {'换手率':>8} {'评分':>6}")
print("-" * 95)

for i, s in enumerate(candidates[:10], 1):
    print(f"{i:<4} {s['code']:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost_100']:>10.0f} {s['change_1d']:>+7.2f}% {s['change_3d']:>+7.2f}% {s['change_5d']:>+7.2f}% {s['turnover']:>7.2f}% {s['score']:>6}")

if candidates:
    print(f"\n{'='*70}")
    print("今日买入方案（超短线）")
    print("=" * 70)
    
    remaining = 1500
    buys = []
    
    for s in candidates[:3]:
        if s['cost_100'] <= remaining:
            buys.append(s)
            remaining -= s['cost_100']
    
    for i, b in enumerate(buys, 1):
        print(f"\n第{i}手: {b['code']} {b['name']}")
        print(f"  价格: {b['price']:.2f}元 × 100股 = {b['cost_100']:.0f}元")
        print(f"  今日涨幅: {b['change_1d']:+.2f}%")
        print(f"  3日涨幅: {b['change_3d']:+.2f}%")
        print(f"  5日涨幅: {b['change_5d']:+.2f}%")
        print(f"  换手率: {b['turnover']:.2f}%")
        print(f"  评分: {b['score']}")
    
    print(f"\n总投入: {1500 - remaining:.0f}元")
    print(f"剩余: {remaining:.0f}元")
    
    print(f"\n{'='*70}")
    print("超短线策略")
    print("=" * 70)
    print("1. T+1: 今天买，明天才能卖")
    print("2. 止损: -5%（跌破立即卖）")
    print("3. 止盈: +15%（达到目标考虑卖）")
    print("4. 明天是周五，卖出后资金下周一可用")
