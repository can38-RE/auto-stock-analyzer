import baostock as bs

bs.login()

print("=" * 70)
print("主板选股筛选器 - 1900元预算")
print("仅限: 主板 (000xxx/001xxx/002xxx/600xxx/601xxx/603xxx)")
print("排除: 创业板(300xxx) | 科创板(688xxx) | 港股")
print("=" * 70)

# Main board codes only
stock_codes = []

# 深交所主板
for i in range(0, 400):
    stock_codes.append(f"sz.{i:06d}")
for i in range(1000, 1100):
    stock_codes.append(f"sz.{i:06d}")
for i in range(2000, 2300):
    stock_codes.append(f"sz.{i:06d}")

# 上交所主板
for i in range(600000, 600400):
    stock_codes.append(f"sh.{i}")
for i in range(601000, 601200):
    stock_codes.append(f"sh.{i}")
for i in range(603000, 603300):
    stock_codes.append(f"sh.{i}")
for i in range(605000, 605100):
    stock_codes.append(f"sh.{i}")

print(f"扫描 {len(stock_codes)} 个主板代码...")

found = []
count = 0

for code in stock_codes:
    count += 1
    if count % 500 == 0:
        print(f"已扫描 {count}...")
    
    try:
        rs = bs.query_history_k_data_plus(
            code, 'date,close,volume,turn',
            start_date='2026-06-16', end_date='2026-06-22',
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
        
        # Filter: Price 5-19 RMB
        if price > 19 or price < 5:
            continue
        
        # Filter: Minimum volume
        if volume < 500000:
            continue
        
        # Calculate momentum
        price_start = float(data[0][1]) if data[0][1] else 0
        momentum = ((price - price_start) / price_start * 100) if price_start > 0 else 0
        
        # Check limit up (主板 10%)
        has_limit = False
        for j in range(1, len(data)):
            prev = float(data[j-1][1]) if data[j-1][1] else 0
            curr = float(data[j][1]) if data[j][1] else 0
            if prev > 0:
                chg = ((curr - prev) / prev) * 100
                if chg >= 9.5:
                    has_limit = True
        
        # Score
        score = 0
        if momentum > 15: score += 30
        elif momentum > 10: score += 20
        elif momentum > 5: score += 10
        elif momentum > 0: score += 5
        
        if has_limit: score += 25
        if turn > 10: score += 15
        elif turn > 5: score += 10
        elif turn > 3: score += 5
        
        # Price sweet spot
        if 10 <= price <= 18: score += 10
        elif 5 <= price < 10: score += 5
        
        cost_100 = price * 100
        
        if score >= 25 and cost_100 <= 1900:
            rs2 = bs.query_stock_basic(code=code)
            name = ""
            while (rs2.error_code == '0') and rs2.next():
                name = rs2.get_row_data()[1]
            
            found.append({
                'code': code.split('.')[1],
                'name': name,
                'price': price,
                'cost': cost_100,
                'momentum': momentum,
                'turnover': turn,
                'limit': has_limit,
                'score': score
            })
    except:
        pass

bs.logout()

found.sort(key=lambda x: -x['score'])

print(f"\n{'='*70}")
print(f"找到 {len(found)} 只符合条件的主板股票:")
print("=" * 70)

print(f"\n{'代码':<10} {'名称':<15} {'价格':>8} {'1手成本':>10} {'动量':>10} {'换手':>8} {'涨停':>6} {'评分':>6}")
print("-" * 80)

for s in found[:20]:
    limit_str = "是" if s['limit'] else "否"
    print(f"{s['code']:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost']:>10.0f} {s['momentum']:>+9.2f}% {s['turnover']:>7.2f}% {limit_str:>6} {s['score']:>6}")

if found:
    print(f"\n{'='*70}")
    print("投资建议:")
    print("=" * 70)
    
    best = found[0]
    print(f"推荐: {best['code']} {best['name']}")
    print(f"价格: {best['price']:.2f}元/股")
    print(f"1手成本: {best['cost']:.0f}元")
    print(f"剩余资金: {1900 - best['cost']:.0f}元")
    print(f"5日动量: {best['momentum']:+.2f}%")
    
    # Check if we can buy 2 stocks
    remaining = 1900 - best['cost']
    second = None
    for s in found[1:]:
        if s['cost'] <= remaining:
            second = s
            break
    
    if second:
        print(f"\n可同时买入第2只: {second['code']} {second['name']}")
        print(f"第2手成本: {second['cost']:.0f}元")
        print(f"两手持仓: {best['cost'] + second['cost']:.0f}元")
        print(f"最终剩余: {1900 - best['cost'] - second['cost']:.0f}元")
