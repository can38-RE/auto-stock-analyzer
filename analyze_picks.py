import baostock as bs

bs.login()

stocks = [
    'sz.301281', 'sz.002281', 'sz.300221', 'sz.301568',
    'sh.603629', 'sz.002080', 'sz.300489', 'sz.300548',
    'sz.301217', 'sh.688379'
]

print("=" * 80)
print("金融分析师6月15日买入股票分析")
print("=" * 80)

for bs_code in stocks:
    print(f"\n{'='*60}")
    
    # Get stock name
    rs = bs.query_stock_basic(code=bs_code)
    name = ""
    while (rs.error_code == '0') and rs.next():
        row = rs.get_row_data()
        name = row[1]
    
    print(f"代码: {bs_code.split('.')[1]} | 名称: {name}")
    
    # Get data from June 10-22
    rs = bs.query_history_k_data_plus(
        bs_code,
        "date,open,high,low,close,volume,amount,turn,peTTM,pbMRQ",
        start_date="2026-06-10",
        end_date="2026-06-22",
        frequency="d",
        adjustflag="3"
    )
    
    data = []
    while (rs.error_code == '0') and rs.next():
        data.append(rs.get_row_data())
    
    if data:
        print(f"{'日期':<12} {'开盘':>8} {'最高':>8} {'最低':>8} {'收盘':>8} {'涨跌%':>8} {'换手%':>8}")
        print("-" * 70)
        
        for i, row in enumerate(data):
            date = row[0]
            open_p = float(row[1]) if row[1] else 0
            high = float(row[2]) if row[2] else 0
            low = float(row[3]) if row[3] else 0
            close = float(row[4]) if row[4] else 0
            turn = float(row[7]) if row[7] else 0
            
            # Calculate change from previous day
            if i > 0:
                prev_close = float(data[i-1][4]) if data[i-1][4] else 0
                chg = ((close - prev_close) / prev_close * 100) if prev_close > 0 else 0
            else:
                chg = 0
            
            print(f"{date:<12} {open_p:>8.2f} {high:>8.2f} {low:>8.2f} {close:>8.2f} {chg:>+7.2f}% {turn:>7.2f}%")
        
        # Show key metrics for June 15
        june15 = None
        for row in data:
            if row[0] == '2026-06-15':
                june15 = row
                break
        
        if june15:
            pe = float(june15[8]) if june15[8] else 0
            pb = float(june15[9]) if june15[9] else 0
            price = float(june15[4]) if june15[4] else 0
            cost_100 = price * 100
            print(f"\n6月15日数据: PE={pe:.1f} | PB={pb:.1f} | 价格={price:.2f} | 1手成本={cost_100:.0f}元")

bs.logout()

print(f"\n{'='*80}")
print("分析完成!")
