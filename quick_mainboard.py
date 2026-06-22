import baostock as bs

bs.login()

print("=" * 70)
print("主板快速扫描 - 1900元预算")
print("仅限: 000xxx/001xxx/002xxx/600xxx/601xxx/603xxx")
print("=" * 70)

# Smaller scan - focus on most common codes
codes = []

# 深交所
for i in range(0, 100):
    codes.append(f"sz.{i:06d}")
for i in range(2000, 2100):
    codes.append(f"sz.{i:06d}")

# 上交所
for i in range(600000, 600100):
    codes.append(f"sh.{i}")
for i in range(601000, 601100):
    codes.append(f"sh.{i}")
for i in range(603000, 603100):
    codes.append(f"sh.{i}")

print(f"扫描 {len(codes)} 个代码...")

found = []

for code in codes:
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
        
        if 5 <= price <= 19 and volume > 500000:
            price_start = float(data[0][1]) if data[0][1] else 0
            momentum = ((price - price_start) / price_start * 100) if price_start > 0 else 0
            
            # Check limit
            has_limit = False
            for j in range(1, len(data)):
                prev = float(data[j-1][1]) if data[j-1][1] else 0
                curr = float(data[j][1]) if data[j][1] else 0
                if prev > 0 and ((curr - prev) / prev * 100) >= 9.5:
                    has_limit = True
            
            score = 0
            if momentum > 15: score += 30
            elif momentum > 10: score += 20
            elif momentum > 5: score += 10
            elif momentum > 0: score += 5
            
            if has_limit: score += 25
            if turn > 10: score += 15
            elif turn > 5: score += 10
            
            if 10 <= price <= 18: score += 10
            
            if score >= 20:
                rs2 = bs.query_stock_basic(code=code)
                name = ""
                while (rs2.error_code == '0') and rs2.next():
                    name = rs2.get_row_data()[1]
                
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

print(f"\n找到 {len(found)} 只主板股票:")
print(f"\n{'代码':<10} {'名称':<15} {'价格':>8} {'1手':>10} {'动量':>10} {'换手':>8} {'涨停':>6} {'评分':>6}")
print("-" * 80)

for s in found[:15]:
    l = "是" if s['limit'] else "否"
    print(f"{s['code']:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost']:>10.0f} {s['momentum']:>+9.2f}% {s['turnover']:>7.2f}% {l:>6} {s['score']:>6}")

if found:
    best = found[0]
    print(f"\n推荐: {best['code']} {best['name']}")
    print(f"价格: {best['price']:.2f}元 | 1手: {best['cost']:.0f}元 | 剩余: {1900-best['cost']:.0f}元")
