import baostock as bs

bs.login()

# Check specific cheap mainboard stocks
codes = [
    'sz.000009', 'sz.000012', 'sz.000014', 'sz.000016', 'sz.000019',
    'sz.000020', 'sz.000021', 'sz.000025', 'sz.000026', 'sz.000028',
    'sz.000029', 'sz.000031', 'sz.000032', 'sz.000034', 'sz.000036',
    'sz.000038', 'sz.000039', 'sz.000040', 'sz.000042', 'sz.000043',
    'sz.000045', 'sz.000046', 'sz.000048', 'sz.000049', 'sz.000050',
    'sz.000055', 'sz.000058', 'sz.000059', 'sz.000060', 'sz.000061',
    'sz.000062', 'sz.000063', 'sz.000065', 'sz.000066', 'sz.000068',
    'sz.000069', 'sz.000070', 'sz.000078', 'sz.000088', 'sz.000089',
    'sz.000090', 'sz.000096', 'sz.000099', 'sz.000100',
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
    'sh.600058', 'sh.600059', 'sh.600060', 'sh.600061',
]

print("=" * 70)
print("主板股票扫描 - 1900元预算")
print("=" * 70)

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
        
        if 5 <= price <= 19 and volume > 100000:
            price_start = float(data[0][1]) if data[0][1] else 0
            momentum = ((price - price_start) / price_start * 100) if price_start > 0 else 0
            
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
            elif turn > 3: score += 5
            
            if 10 <= price <= 18: score += 10
            
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

print(f"\n找到 {len(found)} 只5-19元主板股票:")
print(f"\n{'代码':<10} {'名称':<15} {'价格':>8} {'1手':>10} {'动量':>10} {'换手':>8} {'涨停':>6} {'评分':>6}")
print("-" * 80)

for s in found[:20]:
    l = "是" if s['limit'] else "否"
    print(f"{s['code']:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost']:>10.0f} {s['momentum']:>+9.2f}% {s['turnover']:>7.2f}% {l:>6} {s['score']:>6}")

if found:
    best = found[0]
    print(f"\n{'='*70}")
    print(f"推荐: {best['code']} {best['name']}")
    print(f"价格: {best['price']:.2f}元/股 | 1手: {best['cost']:.0f}元 | 剩余: {1900-best['cost']:.0f}元")
    print(f"动量: {best['momentum']:+.2f}% | 换手: {best['turnover']:.2f}%")
