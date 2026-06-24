import sys
sys.path.insert(0, '.')
from src.analyzers.comprehensive_scorer import get_comprehensive_top_stocks, format_top_stocks_report

stocks = get_comprehensive_top_stocks(budget=1800, top_n=5)
print(format_top_stocks_report(stocks, budget=1800))
