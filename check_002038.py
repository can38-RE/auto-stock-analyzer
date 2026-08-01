import requests

r = requests.get('https://hq.sinajs.cn/list=sz002038', headers={'Referer': 'https://finance.sina.com.cn'}, timeout=5)
d = r.text.split('"')[1].split(',')

price = float(d[3])
prev = float(d[2]) if d[2] else 0
change = ((price - prev) / prev * 100) if prev > 0 else 0

buy_price = 6.43
pnl = (price - buy_price) * 100
pnl_pct = ((price - buy_price) / buy_price) * 100

print("=" * 50)
print("002038 双鹭药业 实时数据")
print("=" * 50)
print(f"当前价: {price:.2f}元")
print(f"今日涨跌: {change:+.2f}%")
print()
print("你的持仓:")
print(f"  买入价: {buy_price:.2f}元")
print(f"  持仓: 100股")
print(f"  成本: 643元")
print(f"  市值: {price * 100:.0f}元")
print(f"  盈亏: {pnl:+.2f}元 ({pnl_pct:+.2f}%)")
