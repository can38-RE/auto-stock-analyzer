import baostock as bs
from datetime import datetime, timedelta

bs.login()

# Target codes - mainboard stocks under 19 RMB
stock_codes = [
    'sz.000009', 'sz.000012', 'sz.000014', 'sz.000016', 'sz.000019',
    'sz.000020', 'sz.000021', 'sz.000025', 'sz.000026', 'sz.000028',
    'sz.000029', 'sz.000031', 'sz.000032', 'sz.000034', 'sz.000036',
    'sz.000038', 'sz.000039', 'sz.000040', 'sz.000042', 'sz.000043',
    'sz.000045', 'sz.000046', 'sz.000048', 'sz.000049', 'sz.000050',
    'sz.000055', 'sz.000058', 'sz.000059', 'sz.000060', 'sz.000061',
    'sz.000062', 'sz.000063', 'sz.000065', 'sz.000066', 'sz.000068',
    'sz.000069', 'sz.000070', 'sz.000078', 'sz.000088', 'sz.000089',
    'sz.000090', 'sz.000096', 'sz.000099', 'sz.000100',
    'sz.000150', 'sz.000151', 'sz.000153', 'sz.000155', 'sz.000156',
    'sz.000157', 'sz.000158', 'sz.000159', 'sz.000160',
    'sz.002001', 'sz.002002', 'sz.002003', 'sz.002004', 'sz.002005',
    'sz.002006', 'sz.002007', 'sz.002008', 'sz.002009', 'sz.002010',
    'sz.002011', 'sz.002012', 'sz.002013', 'sz.002014', 'sz.002015',
    'sz.002016', 'sz.002017', 'sz.002018', 'sz.002019', 'sz.002020',
    'sz.002022', 'sz.002023', 'sz.002024', 'sz.002025', 'sz.002026',
    'sz.002027', 'sz.002028', 'sz.002029', 'sz.002030',
    'sh.600000', 'sh.600004', 'sh.600006', 'sh.600007', 'sh.600008',
    'sh.600009', 'sh.600010', 'sh.600011', 'sh.600012', 'sh.600015',
    'sh.600016', 'sh.600017', 'sh.600018', 'sh.600019', 'sh.600020',
    'sh.600021', 'sh.600022', 'sh.600023', 'sh.600025', 'sh.600026',
    'sh.600027', 'sh.600028', 'sh.600029', 'sh.600030', 'sh.600031',
    'sh.600033', 'sh.600035', 'sh.600036', 'sh.600037', 'sh.600038',
    'sh.600039', 'sh.600048', 'sh.600050', 'sh.600051', 'sh.600052',
    'sh.600053', 'sh.600054', 'sh.600055', 'sh.600056', 'sh.600057',
    'sh.600058', 'sh.600059', 'sh.600060', 'sh.600061', 'sh.600062',
    'sh.600063', 'sh.600064', 'sh.600065', 'sh.600066', 'sh.600067',
    'sh.600068', 'sh.600069', 'sh.600070', 'sh.600071', 'sh.600072',
    'sh.600073', 'sh.600074', 'sh.600075', 'sh.600076', 'sh.600077',
    'sh.600078', 'sh.600079', 'sh.600080', 'sh.600081', 'sh.600082',
    'sh.600083', 'sh.600084', 'sh.600085', 'sh.600086', 'sh.600087',
    'sh.600088', 'sh.600089', 'sh.600090',
]

end_date = "2026-06-23"
start_date = "2026-01-01"  # 6 months

results = []
count = 0

for code in stock_codes:
    count += 1
    if count % 30 == 0:
        print(f"已分析 {count} 只...")
    
    try:
        # Get stock name
        rs = bs.query_stock_basic(code=code)
        name = ""
        while (rs.error_code == '0') and rs.next():
            name = rs.get_row_data()[1]
        
        # Get 6 months of data
        rs = bs.query_history_k_data_plus(
            code,
            'date,open,high,low,close,volume,amount,turn',
            start_date=start_date,
            end_date=end_date,
            frequency='d',
            adjustflag='3'
        )
        
        data = []
        while (rs.error_code == '0') and rs.next():
            data.append(rs.get_row_data())
        
        if len(data) < 60:  # Need at least 60 days of data
            continue
        
        # Parse data
        closes = [float(d[4]) for d in data if d[4]]
        highs = [float(d[2]) for d in data if d[2]]
        lows = [float(d[3]) for d in data if d[3]]
        volumes = [float(d[5]) for d in data if d[5]]
        
        current = closes[-1]
        
        if current > 19 or current < 3:
            continue
        
        # 6-month performance
        start_price = closes[0]
        half_year_return = ((current - start_price) / start_price) * 100
        
        # 1-month performance
        month_ago = closes[-22] if len(closes) >= 22 else closes[0]
        month_return = ((current - month_ago) / month_ago) * 100
        
        # 1-week performance
        week_ago = closes[-5] if len(closes) >= 5 else closes[0]
        week_return = ((current - week_ago) / week_ago) * 100
        
        # Volatility (standard deviation of daily returns)
        daily_returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        avg_return = sum(daily_returns) / len(daily_returns)
        volatility = (sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)) ** 0.5 * 100
        
        # Support and resistance
        recent_20_high = max(highs[-20:])
        recent_20_low = min(lows[-20:])
        recent_60_high = max(highs[-60:])
        recent_60_low = min(lows[-60:])
        
        # Moving averages
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10
        ma20 = sum(closes[-20:]) / 20
        ma60 = sum(closes[-60:]) / 60
        
        # Volume analysis
        avg_vol_20 = sum(volumes[-20:]) / 20
        avg_vol_60 = sum(volumes[-60:]) / 60
        vol_ratio = avg_vol_20 / avg_vol_60 if avg_vol_60 > 0 else 1
        
        # Trend identification
        if current > ma5 > ma10 > ma20:
            trend = "strong_uptrend"
            trend_desc = "强势上涨"
        elif current > ma5 > ma10:
            trend = "uptrend"
            trend_desc = "上涨趋势"
        elif current > ma5:
            trend = "weak_uptrend"
            trend_desc = "弱上涨"
        elif current < ma5 < ma10 < ma20:
            trend = "strong_downtrend"
            trend_desc = "强势下跌"
        elif current < ma5 < ma10:
            trend = "downtrend"
            trend_desc = "下跌趋势"
        elif current < ma5:
            trend = "weak_downtrend"
            trend_desc = "弱下跌"
        else:
            trend = "consolidation"
            trend_desc = "震荡整理"
        
        # Distance from high/low
        dist_from_high = ((current - recent_60_high) / recent_60_high) * 100
        dist_from_low = ((current - recent_60_low) / recent_60_low) * 100
        
        # Score
        score = 50
        if half_year_return > 20: score += 15
        elif half_year_return > 10: score += 10
        elif half_year_return > 0: score += 5
        elif half_year_return < -20: score -= 15
        elif half_year_return < -10: score -= 10
        
        if month_return > 10: score += 10
        elif month_return > 5: score += 5
        elif month_return < -10: score -= 10
        
        if trend in ['strong_uptrend', 'uptrend']: score += 15
        elif trend in ['weak_uptrend']: score += 5
        elif trend in ['downtrend', 'strong_downtrend']: score -= 10
        
        if vol_ratio > 1.5: score += 5  # Volume increasing
        if volatility < 3: score += 5  # Low volatility
        
        cost_100 = current * 100
        
        results.append({
            'code': code.split('.')[1],
            'name': name,
            'price': current,
            'cost_100': cost_100,
            'half_year_return': half_year_return,
            'month_return': month_return,
            'week_return': week_return,
            'volatility': volatility,
            'trend': trend,
            'trend_desc': trend_desc,
            'ma5': ma5,
            'ma10': ma10,
            'ma20': ma20,
            'ma60': ma60,
            'support_20': recent_20_low,
            'resistance_20': recent_20_high,
            'support_60': recent_60_low,
            'resistance_60': recent_60_high,
            'dist_from_high': dist_from_high,
            'dist_from_low': dist_from_low,
            'vol_ratio': vol_ratio,
            'score': score,
        })
        
    except Exception as e:
        pass

bs.logout()

# Sort by score
results.sort(key=lambda x: -x['score'])

# Print results
print("=" * 120)
print("A股主板股票半年深度分析 (1900元预算)")
print("=" * 120)

print(f"\n共分析 {len(results)} 只符合条件的股票\n")

# Print top 30
print(f"{'代码':<10} {'名称':<12} {'价格':>8} {'半年':>8} {'1月':>8} {'1周':>8} {'波动':>8} {'趋势':<12} {'评分':>6}")
print("-" * 100)

for s in results[:30]:
    print(f"{s['code']:<10} {s['name']:<12} {s['price']:>8.2f} {s['half_year_return']:>+7.2f}% {s['month_return']:>+7.2f}% {s['week_return']:>+7.2f}% {s['volatility']:>7.2f}% {s['trend_desc']:<12} {s['score']:>6}")

# Save full results for detailed analysis
import json
with open('stock_analysis_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n完整结果已保存到 stock_analysis_results.json")
