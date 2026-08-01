"""Full market scan - July 2, 2026 with fresh data."""

import baostock as bs
from datetime import datetime, timedelta

bs.login()

today = "2026-07-02"
week_ago = "2026-06-20"

print("=" * 80)
print(f"全市场扫描 - {today} - 最新数据")
print("预算: 1500元 | 策略: 超短线 | 目标: 明天赚100+元")
print("=" * 80)

# Scan ALL mainboard stock codes
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
for i in range(603000, 603300):
    stock_codes.append(f"sh.{i}")
for i in range(605000, 605100):
    stock_codes.append(f"sh.{i}")

print(f"扫描 {len(stock_codes)} 个主板代码...")

candidates = []
count = 0

for code in stock_codes:
    count += 1
    if count % 500 == 0:
        print(f"已扫描 {count}...")
    
    try:
        # Get stock name
        rs = bs.query_stock_basic(code=code)
        name = ""
        while (rs.error_code == '0') and rs.next():
            name = rs.get_row_data()[1]
        
        if not name:
            continue
        
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
        
        # Filter: 3-15 RMB (affordable for 1500 budget)
        if price > 15 or price < 3:
            continue
        
        cost_100 = price * 100
        if cost_100 > 1500:
            continue
        
        # Calculate changes
        change_1d = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) >= 2 else 0
        change_3d = ((closes[-1] - closes[-4]) / closes[-4] * 100) if len(closes) >= 4 else 0
        change_5d = ((closes[-1] - closes[-6]) / closes[-6] * 100) if len(closes) >= 6 else 0
        
        # Score (ultra-short-term focus)
        score = 0
        
        # 1-day momentum (highest weight for ultra-short)
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
        
        # Turnover (liquidity)
        if turn > 10: score += 15
        elif turn > 5: score += 10
        elif turn > 3: score += 5
        
        # Price sweet spot
        if 10 <= price <= 15: score += 10
        elif 5 <= price < 10: score += 5
        
        if score >= 30:
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

# Sort by score
candidates.sort(key=lambda x: -x['score'])

print(f"\n扫描完成！找到 {len(candidates)} 只符合条件的股票")

print(f"\n{'排名':<4} {'代码':<10} {'名称':<15} {'价格':>8} {'1手':>10} {'今日':>8} {'3日':>8} {'5日':>8} {'换手':>8} {'评分':>6}")
print("-" * 95)

for i, s in enumerate(candidates[:15], 1):
    print(f"{i:<4} {s['code']:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost_100']:>10.0f} {s['change_1d']:>+7.2f}% {s['change_3d']:>+7.2f}% {s['change_5d']:>+7.2f}% {s['turnover']:>7.2f}% {s['score']:>6}")

if candidates:
    print(f"\n{'='*80}")
    print("今日买入方案（超短线）")
    print("=" * 80)
    
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
