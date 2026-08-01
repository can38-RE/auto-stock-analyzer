"""Quick stock analysis with correct baostock format."""

import baostock as bs
from datetime import datetime, timedelta

bs.login()

today = datetime.now().strftime("%Y-%m-%d")
week_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

# Correct format: sh.600000, sz.000001
stock_codes = [
    'sz.000100', 'sz.002020', 'sh.600063', 'sh.600076', 'sz.000012',
    'sz.000059', 'sz.000068', 'sz.002023', 'sh.600075', 'sz.002014',
    'sz.002030', 'sh.600073', 'sh.600080', 'sz.000061', 'sz.000089',
    'sz.000060', 'sz.000050', 'sh.600058', 'sz.000066', 'sz.000025',
]

print("=" * 70)
print(f"超短线选股分析 - {today}")
print("策略: 超短线 | 预算: 1500元 | 目标: 明天赚100+元")
print("=" * 70)

candidates = []

for code in stock_codes:
    try:
        # Get stock name
        rs = bs.query_stock_basic(code=code)
        name = ""
        while (rs.error_code == '0') and rs.next():
            name = rs.get_row_data()[1]
        
        # Get historical data
        rs = bs.query_history_k_data_plus(
            code, 'date,close,volume,turn',
            start_date=week_ago, end_date=today,
            frequency='d', adjustflag='3'
        )
        
        data = []
        while (rs.error_code == '0') and rs.next():
            data.append(rs.get_row_data())
        
        if len(data) < 3:
            continue
        
        closes = [float(d[1]) for d in data if d[1]]
        volumes = [float(d[2]) for d in data if d[2]]
        turn = float(data[-1][3]) if data[-1][3] else 0
        
        price = closes[-1]
        
        if price > 15 or price < 3:
            continue
        
        cost_100 = price * 100
        if cost_100 > 1500:
            continue
        
        # Calculate changes
        change_1d = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) >= 2 else 0
        change_3d = ((closes[-1] - closes[-4]) / closes[-4] * 100) if len(closes) >= 4 else 0
        change_5d = ((closes[-1] - closes[-6]) / closes[-6] * 100) if len(closes) >= 6 else 0
        
        # Score
        score = 0
        if change_1d > 5: score += 35
        elif change_1d > 3: score += 25
        elif change_1d > 1: score += 15
        elif change_1d > 0: score += 10
        
        if change_3d > 10: score += 25
        elif change_3d > 5: score += 15
        elif change_3d > 0: score += 10
        
        if change_5d > 15: score += 20
        elif change_5d > 8: score += 15
        elif change_5d > 0: score += 10
        
        if turn > 10: score += 15
        elif turn > 5: score += 10
        
        if 10 <= price <= 15: score += 10
        elif 5 <= price < 10: score += 5
        
        candidates.append({
            'code': code.split('.')[1],
            'name': name,
            'price': price,
            'cost_100': cost_100,
            'change_1d': round(change_1d, 2),
            'change_3d': round(change_3d, 2),
            'change_5d': round(change_5d, 2),
            'turnover': turn,
            'score': score
        })
    except:
        continue

bs.logout()

candidates.sort(key=lambda x: -x['score'])

print(f"\n找到 {len(candidates)} 只符合条件的股票:")
print(f"\n{'排名':<4} {'代码':<10} {'名称':<15} {'价格':>8} {'1手':>10} {'今日':>8} {'3日':>8} {'5日':>8} {'换手':>8} {'评分':>6}")
print("-" * 95)

for i, s in enumerate(candidates[:10], 1):
    print(f"{i:<4} {s['code']:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost_100']:>10.0f} {s['change_1d']:>+7.2f}% {s['change_3d']:>+7.2f}% {s['change_5d']:>+7.2f}% {s['turnover']:>7.2f}% {s['score']:>6}")

if candidates:
    print(f"\n{'='*70}")
    print("今日买入方案")
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
        print(f"  今日: {b['change_1d']:+.2f}% | 3日: {b['change_3d']:+.2f}% | 5日: {b['change_5d']:+.2f}%")
        print(f"  换手率: {b['turnover']:.2f}% | 评分: {b['score']}")
    
    print(f"\n总投入: {1500 - remaining:.0f}元 | 剩余: {remaining:.0f}元")
