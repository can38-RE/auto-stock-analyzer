import sys
sys.path.insert(0, '.')
from src.analyzers.chokepoint import ChokepointAnalyzer
import baostock as bs

analyzer = ChokepointAnalyzer()
stocks = analyzer.get_chokepoint_stocks()

print("=" * 70)
print("Serenity瓶颈理论 - A股标的")
print("核心理念: 'Own the bottleneck, not the brand'")
print("=" * 70)

# Get current prices
bs.login()

print(f"\n{'代码':<10} {'名称':<12} {'价格':>8} {'1手':>10} {'瓶颈层级':<25} {'核心逻辑'}")
print("-" * 90)

affordable = []

for s in stocks:
    code = s['code']
    if code.startswith('6'):
        bs_code = f'sh.{code}'
    else:
        bs_code = f'sz.{code}'
    
    try:
        rs = bs.query_history_k_data_plus(
            bs_code, 'date,close,volume',
            start_date='2026-06-18', end_date='2026-06-23',
            frequency='d', adjustflag='3'
        )
        
        data = []
        while (rs.error_code == '0') and rs.next():
            data.append(rs.get_row_data())
        
        if data:
            price = float(data[-1][1]) if data[-1][1] else 0
            cost_100 = price * 100
            
            print(f"{code:<10} {s['name']:<12} {price:>8.2f} {cost_100:>10.0f} {s['layer_description']:<25} {s['reason']}")
            
            if cost_100 <= 1900:
                affordable.append({
                    'code': code,
                    'name': s['name'],
                    'price': price,
                    'cost_100': cost_100,
                    'layer': s['layer_description'],
                    'reason': s['reason'],
                    'importance': s['importance']
                })
        else:
            print(f"{code:<10} {s['name']:<12} {'N/A':>8} {'N/A':>10} {s['layer_description']:<25} {s['reason']}")
    except Exception as e:
        print(f"{code:<10} {s['name']:<12} {'Error':>8} {'Error':>10} {s['layer_description']:<25} {s['reason']}")

bs.logout()

print(f"\n{'='*70}")
print(f"1900元预算可买入的瓶颈股 ({len(affordable)} 只):")
print("=" * 70)

affordable.sort(key=lambda x: x['cost_100'])

print(f"\n{'代码':<10} {'名称':<12} {'价格':>8} {'1手成本':>10} {'瓶颈层级':<20} {'核心逻辑'}")
print("-" * 85)

for s in affordable:
    print(f"{s['code']:<10} {s['name']:<12} {s['price']:>8.2f} {s['cost_100']:>10.0f} {s['layer']:<20} {s['reason']}")

if affordable:
    print(f"\n{'='*70}")
    print("推荐买入方案:")
    print("=" * 70)
    
    best = affordable[0]
    print(f"首选: {best['code']} {best['name']}")
    print(f"价格: {best['price']:.2f}元 | 1手: {best['cost_100']:.0f}元 | 剩余: {1900 - best['cost_100']:.0f}元")
    print(f"瓶颈层级: {best['layer']}")
    print(f"核心逻辑: {best['reason']}")
    
    remaining = 1900 - best['cost_100']
    for s in affordable[1:]:
        if s['cost_100'] <= remaining:
            print(f"\n可同时买入: {s['code']} {s['name']} ({s['cost_100']:.0f}元)")
            remaining -= s['cost_100']
            break
