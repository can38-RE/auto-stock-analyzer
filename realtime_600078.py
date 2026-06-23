import requests

try:
    # Try Sina Finance API for real-time data
    url = "https://hq.sinajs.cn/list=sh600078"
    headers = {
        "Referer": "https://finance.sina.com.cn",
        "User-Agent": "Mozilla/5.0"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    
    # Parse response
    data = response.text.split('"')[1].split(',')
    
    if len(data) > 10:
        name = data[0]
        open_p = float(data[1])
        yesterday_close = float(data[2])
        current = float(data[3])
        high = float(data[4])
        low = float(data[5])
        volume = float(data[8]) / 100  # Convert to hands
        
        change = ((current - yesterday_close) / yesterday_close) * 100
        
        print("=" * 60)
        print(f"600078 {name} 实时数据")
        print("=" * 60)
        
        print(f"当前价: {current:.2f}元")
        print(f"涨跌幅: {change:+.2f}%")
        print(f"今开: {open_p:.2f}元")
        print(f"最高: {high:.2f}元")
        print(f"最低: {low:.2f}元")
        print(f"成交量: {volume:,.0f}手")
        print(f"昨收: {yesterday_close:.2f}元")
        
        # Calculate P&L
        buy_price = 14.49
        pnl = (current - buy_price) * 100
        pnl_pct = ((current - buy_price) / buy_price) * 100
        
        print(f"\n--- 你的持仓 ---")
        print(f"买入价: {buy_price:.2f}元")
        print(f"当前价: {current:.2f}元")
        print(f"盈亏: {pnl:+.2f}元")
        print(f"盈亏率: {pnl_pct:+.2f}%")
        
        # Key levels
        print(f"\n--- 关键价位 ---")
        print(f"今日最高: {high:.2f}元 (阻力)")
        print(f"今日最低: {low:.2f}元 (支撑)")
        print(f"止损位: {buy_price * 0.95:.2f}元 (-5%)")
        print(f"止盈位: {buy_price * 1.10:.2f}元 (+10%)")
        
        # Strategy
        print(f"\n--- 明日策略 ---")
        if current > buy_price:
            print("当前盈利，可考虑:")
            print("  1. 继续持有，目标15.50元")
            print("  2. 若冲高到15.00以上，减仓一半")
            print("  3. 止损设在14.00元")
        else:
            print("当前亏损，注意:")
            print("  1. 止损位: 13.80元")
            print("  2. 若跌破止损，果断卖出")
            print("  3. 不要补仓摊低成本")
    else:
        print("数据解析失败")
        
except Exception as e:
    print(f"获取实时数据失败: {e}")
    print("可能是网络问题")
