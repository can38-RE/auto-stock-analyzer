import baostock as bs

bs.login()

print("=" * 60)
print("快速扫描 - 1900元预算股票")
print("=" * 60)

# Check specific ranges
ranges = [
    (300000, 300050),
    (301000, 301050),
    (300200, 300250),
    (301200, 301250),
    (2000, 2050),
    (3000, 3050),
]

found = []

for start, end in ranges:
    for i in range(start, end):
        if start >= 300000:
            code = f"sz.{i}"
        else:
            code = f"sz.{i:06d}"
        
        try:
            rs = bs.query_history_k_data_plus(
                code, 'date,close,volume,turn',
                start_date='2026-06-16', end_date='2026-06-22',
                frequency='d', adjustflag='3'
            )
            
            data = []
            while (rs.error_code == '0') and rs.next():
                data.append(rs.get_row_data())
            
            if len(data) >= 2:
                latest = data[-1]
                price = float(latest[1]) if latest[1] else 0
                volume = float(latest[2]) if latest[2] else 0
                turn = float(latest[3]) if latest[3] else 0
                
                if 5 <= price <= 19 and volume > 500000:
                    price_start = float(data[0][1]) if data[0][1] else 0
                    momentum = ((price - price_start) / price_start * 100) if price_start > 0 else 0
                    
                    # Check limit up
                    has_limit = False
                    for j in range(1, len(data)):
                        prev = float(data[j-1][1]) if data[j-1][1] else 0
                        curr = float(data[j][1]) if data[j][1] else 0
                        if prev > 0:
                            chg = ((curr - prev) / prev) * 100
                            if chg >= 19.5:
                                has_limit = True
                    
                    rs2 = bs.query_stock_basic(code=code)
                    name = ""
                    while (rs2.error_code == '0') and rs2.next():
                        name = rs2.get_row_data()[1]
                    
                    score = 0
                    if momentum > 15: score += 30
                    elif momentum > 10: score += 20
                    elif momentum > 5: score += 10
                    elif momentum > 0: score += 5
                    
                    if has_limit: score += 25
                    if turn > 10: score += 15
                    elif turn > 5: score += 10
                    
                    if code.startswith('sz.30'):
                        score += 10
                    
                    if 10 <= price <= 18:
                        score += 10
                    
                    found.append({
                        'code': code.split('.')[1],
                        'name': name,
                        'price': price,
                        'cost': price * 100,
                        'momentum': momentum,
                        'turnover': turn,
                        'limit': has_limit,
                        'score': score
                    })
        except:
            pass

bs.logout()

found.sort(key=lambda x: -x['score'])

print(f"\n找到 {len(found)} 只符合条件的股票:")
print(f"\n{'代码':<10} {'名称':<15} {'价格':>8} {'1手':>10} {'动量':>10} {'换手':>8} {'涨停':>6} {'评分':>6}")
print("-" * 85)

for s in found[:15]:
    limit_str = "是" if s['limit'] else "否"
    print(f"{s['code']:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost']:>10.0f} {s['momentum']:>+9.2f}% {s['turnover']:>7.2f}% {limit_str:>6} {s['score']:>6}")

if found:
    best = found[0]
    print(f"\n推荐买入: {best['code']} {best['name']}")
    print(f"价格: {best['price']:.2f}元/股")
    print(f"1手成本: {best['cost']:.0f}元")
    print(f"剩余资金: {1900 - best['cost']:.0f}元")
