import requests

try:
    r = requests.get('https://hq.sinajs.cn/list=sh600078', 
                     headers={'Referer': 'https://finance.sina.com.cn'}, 
                     timeout=10)
    d = r.text.split('"')[1].split(',')
    
    current = float(d[3])
    yesterday = float(d[2])
    high = float(d[4])
    low = float(d[5])
    
    buy_price = 14.49
    shares = 100
    
    pnl = (current - buy_price) * shares
    pnl_pct = ((current - buy_price) / buy_price) * 100
    total_value = current * shares
    
    print("=" * 50)
    print("600078 澄星股份 实时数据")
    print("=" * 50)
    print(f"当前价: {current:.2f}元")
    print(f"今日涨跌: {((current-yesterday)/yesterday)*100:+.2f}%")
    print(f"最高: {high:.2f}元 | 最低: {low:.2f}元")
    print()
    print("=" * 50)
    print("你的持仓")
    print("=" * 50)
    print(f"买入价: {buy_price:.2f}元")
    print(f"持仓: {shares}股")
    print(f"成本: {buy_price * shares:.0f}元")
    print(f"市值: {total_value:.0f}元")
    print(f"盈亏: {pnl:+.2f}元 ({pnl_pct:+.2f}%)")
    print()
    
    # Decision
    print("=" * 50)
    print("操作建议")
    print("=" * 50)
    
    if pnl_pct <= -5:
        print("[警告] 亏损超过5%，建议止损!")
        print(f"止损价: {buy_price * 0.95:.2f}元")
        print("建议: 果断卖出，保住本金")
    elif pnl_pct <= -3:
        print("[注意] 亏损3-5%，密切关注")
        print(f"止损价: {buy_price * 0.95:.2f}元")
        print("建议: 设好止损，跌破就卖")
    elif pnl_pct < 0:
        print("[观望] 小幅亏损")
        print("建议: 继续持有，等待反弹")
    elif pnl_pct < 5:
        print("[持有] 小幅盈利")
        print("建议: 继续持有，目标+10%")
    else:
        print("[止盈] 盈利较多")
        print("建议: 可考虑减仓一半")
    
except Exception as e:
    print(f"获取数据失败: {e}")
