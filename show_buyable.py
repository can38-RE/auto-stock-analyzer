import sys
sys.path.insert(0, '.')
from src.collectors.mainboard_screener import MainboardScreener

screener = MainboardScreener()
stocks = screener.screen_stocks(budget=1900, top_n=20)

# Keywords related to chokepoint layers
chokepoint_keywords = {
    "原材料": ["黄金", "有色", "稀土", "矿业", "金属"],
    "半导体材料": ["新材", "电子", "科技", "化学"],
    "先进封装": ["电子", "科技", "微"],
    "光通信": ["通信", "光", "网络", "信息"],
    "AI芯片": ["智能", "科技", "信息", "电子"],
    "设备": ["设备", "机械", "仪器"],
    "算力": ["信息", "数据", "计算", "网络"],
}

print("=" * 70)
print("1900元预算 - 主板股票（含瓶颈产业链关联）")
print("=" * 70)

print(f"\n{'代码':<10} {'名称':<15} {'价格':>8} {'1手':>10} {'涨跌':>8} {'换手':>8} {'评分':>6} {'产业链关联'}")
print("-" * 95)

for s in stocks:
    # Check if related to chokepoint
    related = ""
    name = s['name']
    for layer, keywords in chokepoint_keywords.items():
        if any(kw in name for kw in keywords):
            related = layer
            break
    
    related_str = f"← {related}" if related else ""
    print(f"{s['code']:<10} {s['name']:<15} {s['price']:>8.2f} {s['cost_100']:>10.0f} {s['change']:>+7.2f}% {s['turnover']:>7.2f}% {s['score']:>6} {related_str}")

# Buy plan
buy_plan = screener.generate_buy_plan(stocks, budget=1900)

print(f"\n{'='*70}")
print("买入方案:")
print("=" * 70)

if buy_plan['positions']:
    for i, pos in enumerate(buy_plan['positions'], 1):
        print(f"第{i}手: {pos['code']} {pos['name']}")
        print(f"  价格: {pos['price']:.2f}元 × 100股 = {pos['cost']}元")
        print(f"  涨跌: {pos['change']:+.2f}% | 评分: {pos['score']}")
    
    print(f"\n总投入: {buy_plan['total_cost']}元")
    print(f"剩余: {buy_plan['remaining']}元")
