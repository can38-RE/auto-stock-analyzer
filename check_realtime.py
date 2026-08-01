"""Check real-time prices for recommended stocks."""

from datetime import datetime
import requests

stocks = [
    ("000100", "TCL科技"),
    ("002038", "双鹭药业"),
    ("600063", "皖维高新"),
    ("603212", "赛伍技术"),
    ("002053", "云南投资"),
    ("002020", "京新药业"),
    ("002268", "卫士通"),
]

print("=" * 60)
print(f"实时价格查询 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print("=" * 60)

for code, name in stocks:
    try:
        if code.startswith('6'):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"
        
        url = f"https://hq.sinajs.cn/list={symbol}"
        response = requests.get(url, headers={'Referer': 'https://finance.sina.com.cn'}, timeout=5)
        
        if response.status_code == 200:
            data = response.text.split('"')[1].split(',')
            if len(data) > 3:
                price = float(data[3])
                prev_close = float(data[2]) if data[2] else 0
                change_pct = ((price - prev_close) / prev_close * 100) if prev_close > 0 else 0
                
                print(f"\n{code} {name}")
                print(f"  当前价: {price:.2f}元")
                print(f"  涨跌: {change_pct:+.2f}%")
                print(f"  1手成本: {price * 100:.0f}元")
    except:
        pass

print(f"\n{'='*60}")
print("注意：以上为实时数据，价格随时变化")
