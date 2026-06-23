import sys
sys.path.insert(0, '.')
from src.analyzers.trend import TrendAnalyzer, format_trend_analysis

analyzer = TrendAnalyzer()

# Top stocks from screener
stocks = [
    {'code': '600078', 'name': '澄星股份', 'price': 14.61},
    {'code': '000060', 'name': '中金岭南', 'price': 8.81},
    {'code': '002023', 'name': '海特高新', 'price': 13.28},
    {'code': '600063', 'name': '皖维高新', 'price': 8.85},
    {'code': '000066', 'name': '中国长城', 'price': 18.48},
]

print("=" * 70)
print("今日走势分析 + 入场策略")
print("=" * 70)

for stock in stocks:
    analysis = analyzer.analyze_stock(stock['code'], stock['name'])
    
    if analysis:
        trend = analysis['trend']
        strategy = analysis['strategy']
        entry = analysis['entry_prices']
        sr = analysis['support_resistance']
        
        print(f"\n{'='*60}")
        print(f"[{stock['name']}] ({stock['code']})")
        print(f"{'='*60}")
        print(f"当前价: {analysis['current_price']}元 | 今日: {analysis['today_change']:+.2f}%")
        print(f"趋势: {trend['description']}")
        print(f"  MA5={trend['ma5']} | MA10={trend['ma10']} | MA20={trend['ma20']}")
        print(f"支撑: {sr['support']}元 | 阻力: {sr['resistance']}元 | 波动: {sr['range_pct']}%")
        
        print(f"\n>>> 入场策略: {strategy['type']}")
        print(f"  建议动作: {strategy['action']}")
        print(f"  入场价: {strategy['entry_price']}元")
        print(f"  风险等级: {strategy['risk_level']}")
        
        print(f"\n--- 分级入场价 ---")
        print(f"  激进: {entry['aggressive']}元 (当前-1%)")
        print(f"  稳健: {entry['moderate']}元 (当前-3%)")
        print(f"  保守: {entry['conservative']}元 (支撑位)")
        print(f"  突破: {entry['breakout']}元 (阻力+1%)")
        
        print(f"\n--- 风控 ---")
        print(f"  止损: {entry['stop_loss']}元 (-7%)")
        print(f"  止盈1: {entry['take_profit_1']}元 (+10%)")
        print(f"  止盈2: {entry['take_profit_2']}元 (+20%)")
        
        print(f"\n--- 操作要点 ---")
        for tip in strategy['tips']:
            print(f"  * {tip}")
