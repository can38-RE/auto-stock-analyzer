import baostock as bs
from datetime import datetime

bs.login()

today = "2026-06-18"  # Latest trading day
yesterday = "2026-06-17"

# Get all stocks
rs = bs.query_stock_basic(code_name="")

stocks = []
while (rs.error_code == '0') and rs.next():
    row = rs.get_row_data()
    code = row[0]
    name = row[1]
    status = row[4]
    
    if status == '1':  # Active stocks
        stocks.append((code, name))

print(f"查询 {len(stocks)} 只股票...")

limit_up = []
limit_down = []
count = 0

for code, name in stocks:
    count += 1
    if count % 500 == 0:
        print(f"已查询 {count} 只...")
    
    try:
        rs = bs.query_history_k_data_plus(
            code,
            "date,close,preclose,pctChg",
            start_date=yesterday,
            end_date=today,
            frequency="d",
            adjustflag="3"
        )
        
        data = []
        while (rs.error_code == '0') and rs.next():
            data.append(rs.get_row_data())
        
        if len(data) >= 2:
            latest = data[-1]
            prev = data[-2]
            
            close = float(latest[1]) if latest[1] else 0
            preclose = float(latest[2]) if latest[2] else 0
            pct_chg = float(latest[3]) if latest[3] else 0
            
            # Check if it's the target date
            if latest[0] == today:
                # Determine limit threshold
                if code.startswith('sh.688') or code.startswith('sz.30'):
                    # 科创板/创业板: 20% limit
                    limit_threshold = 19.9
                elif code.startswith('sh.8') or code.startswith('sz.8'):
                    # 北交所: 30% limit
                    limit_threshold = 29.9
                else:
                    # 主板: 10% limit
                    limit_threshold = 9.9
                
                if pct_chg >= limit_threshold:
                    limit_up.append((code, name, pct_chg, close))
                elif pct_chg <= -limit_threshold:
                    limit_down.append((code, name, pct_chg, close))
    except Exception:
        pass

bs.logout()

print(f"\n{'='*60}")
print(f"日期: {today}")
print(f"{'='*60}")

print(f"\n涨停股票 ({len(limit_up)} 只):")
print(f"{'代码':<12} {'名称':<15} {'涨跌幅':>10} {'收盘价':>10}")
print("-" * 50)
for code, name, chg, close in sorted(limit_up, key=lambda x: -x[2]):
    print(f"{code:<12} {name:<15} {chg:>9.2f}% {close:>10.2f}")

print(f"\n跌停股票 ({len(limit_down)} 只):")
print(f"{'代码':<12} {'名称':<15} {'涨跌幅':>10} {'收盘价':>10}")
print("-" * 50)
for code, name, chg, close in sorted(limit_down, key=lambda x: x[2]):
    print(f"{code:<12} {name:<15} {chg:>9.2f}% {close:>10.2f}")

print(f"\n总结: 涨停 {len(limit_up)} 只, 跌停 {len(limit_down)} 只")
