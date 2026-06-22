import baostock as bs
import pandas as pd

bs.login()

stocks = [
    ('sz.002837', '002837'),
    ('sh.688017', '688017'),
    ('sz.002281', '002281'),
    ('sz.301568', '301568')
]

for bs_code, code in stocks:
    print(f'\n{"="*50}')
    print(f'股票代码: {code}')
    
    # Get basic info
    rs = bs.query_stock_basic(code=bs_code)
    while (rs.error_code == '0') and rs.next():
        row = rs.get_row_data()
        print(f'股票名称: {row[1]}')
        print(f'上市状态: {row[4]}')
    
    # Get latest quote
    rs = bs.query_history_k_data_plus(
        bs_code,
        'date,open,high,low,close,volume,amount,turn,peTTM,pbMRQ',
        start_date='2026-06-15',
        end_date='2026-06-22',
        frequency='d',
        adjustflag='3'
    )
    
    data = []
    while (rs.error_code == '0') and rs.next():
        data.append(rs.get_row_data())
    
    if data:
        latest = data[-1]
        print(f'最新日期: {latest[0]}')
        print(f'开盘价: {latest[1]}')
        print(f'最高价: {latest[2]}')
        print(f'最低价: {latest[3]}')
        print(f'收盘价: {latest[4]}')
        print(f'成交量: {latest[5]}')
        print(f'成交额: {latest[6]}')
        print(f'换手率: {latest[7]}')
        print(f'PE(TTM): {latest[8]}')
        print(f'PB(MRQ): {latest[9]}')
        
        # Calculate change
        if len(data) >= 2:
            prev_close = float(data[-2][4]) if data[-2][4] else 0
            curr_close = float(latest[4]) if latest[4] else 0
            if prev_close > 0:
                change = ((curr_close - prev_close) / prev_close) * 100
                print(f'涨跌幅: {change:.2f}%')
    else:
        print('无交易数据')

bs.logout()
print('\n查询完成!')
