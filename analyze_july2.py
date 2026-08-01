"""Today's full market analysis - July 2, 2026 (Thursday)"""

import baostock as bs
from datetime import datetime, timedelta

bs.login()

today = "2026-07-02"
week_ago = "2026-06-20"

print("=" * 70)
print(f"全市场分析 - {today} 周四")
print("策略: 超短线 | 预算: 1500元 | 目标: 周五赚100+元")
print("=" * 70)

stock_codes = [
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

candidates = []

for code in stock_codes:
    try:
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
        
        latest = data[-1]
        price = float(latest[1]) if latest[1] else 0
        volume = float(latest[2]) if latest[2] else 0
        turn = float(latest[3]) if latest[3] else 0
        
        if price > 15 or price < 3:
            continue
        
        if volume < 500000:
            continue
        
        closes = [float(d[1]) for d in data if d[1]]
        change_1d = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) >= 2 else 0
        change_3d = ((closes[-1] - closes[-4]) / closes[-4] * 100) if len(closes) >= 4 else 0
        
        # Score
        score = 0
        if change_1d > 5: score += 30
        elif change_1d > 3: score += 20
        elif change_1d > 1: score += 15
        elif change_1d > 0: score += 10
        
        if change_3d > 10: score += 25
        elif change_3d > 5: score += 15
        elif change_3d > 0: score += 10
        
        if turn > 10: score += 15
        elif turn > 5: score += 10
        
        if volume > 5000000: score += 10
        
        rs2 = bs.query_stock_basic(code=code)
        name = ""
        while (rs2.error_code == '0') and rs2.next():
            name = rs2.get_row_data()[1]
        
        cost_100 = price * 100
        
        if score >= 30 and cost_100 <= 1500:
            candidates.append({
                'code': code.split('.')[1],
                'name': name,
                'price': price,
                'cost_100': cost_100,
                'change_1d': round(change_1d, 2),
                'change_3d': round(change_3d, 2),
                'turnover': turn,
                'score': score
            })
    except:
        pass

bs.logout()

candidates.sort(key=lambda x: -x['score'])

print(f"\n找到 {len(candidates)} 只符合条件的股票:")
print(f"\n{'排名':<4} {'代码':<10} {'名称':<15} {'价格':>8} {'1手成本':>10} {'今日涨跌':>10} {'3日涨跌':>10} {'换手率':>8} {'评分':>6}")
print("-" * 90)

for i, s in enumerate(candidates[:15], 1):
    print(f"{i:<4} {s['code']:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost_100']:>10.0f} {s['change_1d']:>+9.2f}% {s['change_3d']:>+9.2f}% {s['turnover']:>7.2f}% {s['score']:>6}")

if candidates:
    best = candidates[0]
    second = candidates[1] if len(candidates) > 1 else None
    
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
        print(f"  今日涨幅: {b['change_1d']:+.2f}%")
        print(f"  3日涨幅: {b['change_3d']:+.2f}%")
        print(f"  评分: {b['score']}")
    
    print(f"\n总投入: {1500 - remaining:.0f}元")
    print(f"剩余: {remaining:.0f}元")
    
    print(f"\n{'='*70}")
    print("超短线策略提醒")
    print("=" * 70)
    print("1. T+1规则: 今天买，明天才能卖")
    print("2. 止损: -5%（跌破立即卖出）")
    print("3. 止盈: +15%（达到目标考虑卖出）")
    print("4. 持仓: 最多1-2只，集中优势")
    print("5. 明天是周五，卖出后资金下周一可用")
