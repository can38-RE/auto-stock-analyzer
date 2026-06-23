import baostock as bs

bs.login()

# Get today's data (June 23, 2026)
rs = bs.query_history_k_data_plus(
    'sh.600078',
    'date,open,high,low,close,volume,amount,turn',
    start_date='2026-06-23',
    end_date='2026-06-23',
    frequency='d',
    adjustflag='3'
)

data = []
while (rs.error_code == '0') and rs.next():
    data.append(rs.get_row_data())

print("=" * 60)
print("600078 澄星股份 今日数据 (2026-06-23)")
print("=" * 60)

if data:
    row = data[0]
    open_p = float(row[1])
    high = float(row[2])
    low = float(row[3])
    close = float(row[4])
    volume = float(row[5])
    
    print(f"开盘价: {open_p:.2f}元")
    print(f"最高价: {high:.2f}元")
    print(f"最低价: {low:.2f}元")
    print(f"收盘价: {close:.2f}元")
    print(f"成交量: {volume:,.0f}手")
    
    # Calculate change from yesterday
    yesterday_close = 14.61  # Yesterday's close
    change = ((close - yesterday_close) / yesterday_close) * 100
    
    print(f"\n涨跌幅: {change:+.2f}%")
    print(f"买入价: 14.49元")
    print(f"盈亏: {(close - 14.49) * 100:+.2f}元 (100股)")
    print(f"盈亏率: {((close - 14.49) / 14.49) * 100:+.2f}%")
    
    # Key levels
    print(f"\n关键价位:")
    print(f"  今日最高: {high:.2f}元")
    print(f"  今日最低: {low:.2f}元")
    print(f"  支撑位: {low:.2f}元")
    print(f"  阻力位: {high:.2f}元")
else:
    print("今日数据暂未获取到")

bs.logout()
