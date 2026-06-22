import baostock as bs

bs.login()

print("=" * 80)
print("激进选股筛选器 - 1900元预算")
print("=" * 80)

# Focus on common stock code ranges
stock_codes = []

# SH main board
for i in range(600000, 600300):
    stock_codes.append(f"sh.{i}")
for i in range(601000, 601200):
    stock_codes.append(f"sh.{i}")
for i in range(603000, 603200):
    stock_codes.append(f"sh.{i}")

# SZ main board
for i in range(0, 500):
    stock_codes.append(f"sz.{i:06d}")
for i in range(2000, 2200):
    stock_codes.append(f"sz.{i:06d}")

# 创业板 (ChiNext)
for i in range(300000, 300300):
    stock_codes.append(f"sz.{i}")
for i in range(301000, 301300):
    stock_codes.append(f"sz.{i}")

# 科创板 (STAR)
for i in range(688000, 688100):
    stock_codes.append(f"sh.{i}")

print(f"扫描 {len(stock_codes)} 个代码...")

candidates = []
count = 0

for code in stock_codes:
    count += 1
    if count % 500 == 0:
        print(f"已扫描 {count}...")
    
    try:
        rs = bs.query_history_k_data_plus(
            code,
            "date,close,volume,turn",
            start_date="2026-06-16",
            end_date="2026-06-22",
            frequency="d",
            adjustflag="3"
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
        if volume < 1000000:
            continue
        
        # Calculate momentum
        price_start = float(data[0][1]) if data[0][1] else 0
        momentum = ((price - price_start) / price_start * 100) if price_start > 0 else 0
        
        # Check limit up
        has_limit_up = False
        for i in range(1, len(data)):
            prev = float(data[i-1][1]) if data[i-1][1] else 0
            curr = float(data[i][1]) if data[i][1] else 0
            if prev > 0:
                chg = ((curr - prev) / prev) * 100
                if code.startswith('sz.30') or code.startswith('sh.688'):
                    if chg >= 19.5: has_limit_up = True
                else:
                    if chg >= 9.5: has_limit_up = True
        
        # Score
        score = 0
        if momentum > 15: score += 30
        elif momentum > 10: score += 20
        elif momentum > 5: score += 10
        elif momentum > 0: score += 5
        
        if has_limit_up: score += 25
        if turn > 10: score += 15
        elif turn > 5: score += 10
        
        if code.startswith('sz.30') or code.startswith('sh.688'):
            score += 10
        
        if 10 <= price <= 18: score += 10
        
        cost_100 = price * 100
        
        if score >= 25 and cost_100 <= 1900:
            rs2 = bs.query_stock_basic(code=code)
            name = ""
            while (rs2.error_code == '0') and rs2.next():
                name = rs2.get_row_data()[1]
            
            candidates.append({
                'code': code,
                'name': name,
                'price': price,
                'cost_100': cost_100,
                'momentum': momentum,
                'turnover': turn,
                'limit_up': has_limit_up,
                'score': score
            })
    except:
        pass

bs.logout()

candidates.sort(key=lambda x: -x['score'])

print(f"\n{'='*80}")
print(f"1900元预算可买入的股票 ({len(candidates)} 只):")
print("=" * 80)

print(f"\n{'代码':<10} {'名称':<15} {'价格':>8} {'1手成本':>10} {'动量':>10} {'换手':>8} {'涨停':>6} {'评分':>6}")
print("-" * 85)

for s in candidates[:20]:
    limit = "是" if s['limit_up'] else "否"
    print(f"{s['code'].split('.')[1]:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost_100']:>10.0f} {s['momentum']:>+9.2f}% {s['turnover']:>7.2f}% {limit:>6} {s['score']:>6}")

if candidates:
    best = candidates[0]
    print(f"\n推荐: {best['code'].split('.')[1]} {best['name']}")
    print(f"价格: {best['price']:.2f}元 | 1手: {best['cost_100']:.0f}元 | 剩余: {1900-best['cost_100']:.0f}元")
