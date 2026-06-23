import baostock as bs

bs.login()

rs = bs.query_history_k_data_plus(
    'sh.600078',
    'date,open,high,low,close,volume',
    start_date='2026-06-16',
    end_date='2026-06-23',
    frequency='d',
    adjustflag='3'
)

data = []
while (rs.error_code == '0') and rs.next():
    data.append(rs.get_row_data())

print("=" * 60)
print("600078 澄星股份 近期走势")
print("=" * 60)
print(f"{'日期':<12} {'开盘':>8} {'最高':>8} {'最低':>8} {'收盘':>8}")
print("-" * 50)

for row in data:
    print(f"{row[0]:<12} {float(row[1]):>8.2f} {float(row[2]):>8.2f} {float(row[3]):>8.2f} {float(row[4]):>8.2f}")

# Calculate key levels
closes = [float(d[4]) for d in data]
highs = [float(d[2]) for d in data]
lows = [float(d[3]) for d in data]

support = min(lows[-5:])
resistance = max(highs[-5:])
ma5 = sum(closes[-5:]) / 5

print(f"\n关键价位:")
print(f"  支撑位: {support:.2f}元")
print(f"  阻力位: {resistance:.2f}元")
print(f"  MA5: {ma5:.2f}元")
print(f"  买入价: 14.49元")

bs.logout()
