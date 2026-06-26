"""Comprehensive stock scoring with proper weights."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger


# Scoring weights (must sum to 100)
WEIGHTS = {
    "technical": 25,    # Technical analysis (trend, momentum)
    "fundamental": 25,  # Fundamental analysis (ROE, margins, PE)
    "policy": 20,       # Policy alignment
    "volume": 15,       # Volume and liquidity
    "price": 10,        # Price position
    "metaphysics": 5,   # Metaphysics (smallest weight)
}


def _calculate_holding_recommendation(change_1d, change_5d, change_10d, turnover, roe, price):
    """Calculate holding recommendation based on multiple factors."""
    # Base holding days based on momentum
    if change_5d > 15:
        base_days = 1
        strategy = "超短线"
        reason = "涨幅过大，及时止盈"
    elif change_5d > 10:
        base_days = 2
        strategy = "短线"
        reason = "强势股，跟随趋势"
    elif change_5d > 5:
        base_days = 3
        strategy = "短波段"
        reason = "上涨趋势，持有待涨"
    elif change_5d > 0:
        base_days = 5
        strategy = "波段"
        reason = "温和上涨，耐心持有"
    else:
        base_days = 0
        strategy = "观望"
        reason = "下跌趋势，不建议买入"
    
    # Adjust based on turnover
    if turnover > 15:
        base_days = max(1, base_days - 2)
        reason += "，换手率高需谨慎"
    elif turnover > 10:
        base_days = max(1, base_days - 1)
    
    # Adjust based on ROE
    if roe and roe > 15:
        base_days += 1
        reason += "，基本面优秀可延长"
    
    # Adjust based on price level
    if price < 10:
        base_days += 1
        reason += "，低价股弹性大"
    
    # Generate sell signals
    sell_signals = []
    if change_1d > 5:
        sell_signals.append("当日涨幅超5%，考虑止盈")
    if change_5d > 15:
        sell_signals.append("5日涨幅超15%，高位减仓")
    sell_signals.append(f"跌破买入价{max(5, abs(change_5d)):.0f}%止损")
    sell_signals.append("连续2天阴线考虑卖出")
    
    # Format holding period
    if base_days <= 0:
        period = "不建议买入"
    elif base_days == 1:
        period = "T+1次日卖出"
    elif base_days <= 3:
        period = f"{base_days}天（{strategy}）"
    else:
        period = f"{base_days-2}-{base_days}天（{strategy}）"
    
    return {
        "period": period,
        "min_days": max(1, base_days - 2),
        "max_days": base_days,
        "strategy": strategy,
        "reason": reason,
        "sell_signals": sell_signals[:3]
    }


def get_comprehensive_top_stocks(budget: float = 1800, top_n: int = 10) -> List[Dict[str, Any]]:
    """Get top stocks with comprehensive scoring."""
    try:
        import baostock as bs
        
        bs.login()
        logger.info("Fetching stock data via baostock...")
        
        # Use dynamic dates
        today = datetime.now()
        end_date = today.strftime("%Y-%m-%d")
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        
        logger.info(f"Date range: {start_date} to {end_date}")
        
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
        
        # Policy-aligned sectors
        policy_sectors = {
            "新能源": ["光伏", "风电", "储能", "锂电", "新能源", "阳光"],
            "人工智能": ["AI", "智能", "科技", "信息", "数据"],
            "半导体": ["芯片", "半导体", "电子", "集成电路"],
            "新材料": ["新材", "材料", "化工"],
            "高端制造": ["制造", "机械", "装备", "自动化"],
        }
        
        candidates = []
        count = 0
        
        for code in stock_codes:
            count += 1
            if count % 50 == 0:
                logger.info(f"Scanned {count} stocks...")
            
            try:
                # Get price data
                rs = bs.query_history_k_data_plus(
                    code, 'date,close,volume,turn',
                    start_date=start_date, end_date=end_date,
                    frequency='d', adjustflag='3'
                )
                
                data = []
                while (rs.error_code == '0') and rs.next():
                    data.append(rs.get_row_data())
                
                if len(data) < 5:
                    continue
                
                latest = data[-1]
                price = float(latest[1]) if latest[1] else 0
                volume = float(latest[2]) if latest[2] else 0
                turn = float(latest[3]) if latest[3] else 0
                
                if price > 19 or price < 3:
                    continue
                
                cost_100 = price * 100
                if cost_100 > budget:
                    continue
                
                # Get stock name
                rs2 = bs.query_stock_basic(code=code)
                name = ""
                while (rs2.error_code == '0') and rs2.next():
                    name = rs2.get_row_data()[1]
                
                # Calculate technical score (25%)
                closes = [float(d[1]) for d in data if d[1]]
                change_1d = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) >= 2 else 0
                change_5d = ((closes[-1] - closes[-5]) / closes[-5] * 100) if len(closes) >= 5 else 0
                change_10d = ((closes[-1] - closes[-10]) / closes[-10] * 100) if len(closes) >= 10 else 0
                
                technical_score = 0
                if change_1d > 3: technical_score += 30
                elif change_1d > 1: technical_score += 20
                elif change_1d > 0: technical_score += 10
                
                if change_5d > 10: technical_score += 40
                elif change_5d > 5: technical_score += 30
                elif change_5d > 0: technical_score += 20
                
                if change_10d > 15: technical_score += 30
                elif change_10d > 8: technical_score += 20
                elif change_10d > 0: technical_score += 10
                
                technical_score = min(technical_score, 100)
                
                # Calculate fundamental score (25%)
                fundamental_score = 50
                
                roe = 0
                gp_margin = 0
                try:
                    rs3 = bs.query_profit_data(code=code, year=2024, quarter=4)
                    while rs3.next():
                        row = rs3.get_row_data()
                        if row and len(row) > 5:
                            roe = float(row[3]) * 100 if row[3] else 0
                            gp_margin = float(row[5]) * 100 if row[5] else 0
                except:
                    pass
                
                if roe > 15: fundamental_score += 25
                elif roe > 10: fundamental_score += 15
                elif roe > 5: fundamental_score += 10
                
                if gp_margin > 30: fundamental_score += 25
                elif gp_margin > 20: fundamental_score += 15
                elif gp_margin > 10: fundamental_score += 10
                
                fundamental_score = min(fundamental_score, 100)
                
                # Calculate policy score (20%)
                policy_score = 50
                for sector, keywords in policy_sectors.items():
                    if any(kw in name for kw in keywords):
                        policy_score = 90
                        break
                
                # Calculate volume score (15%)
                volume_score = 50
                if turn > 10: volume_score = 90
                elif turn > 5: volume_score = 75
                elif turn > 3: volume_score = 60
                
                # Calculate price position score (10%)
                price_score = 50
                if 10 <= price <= 15: price_score = 90
                elif 5 <= price < 10: price_score = 70
                elif 15 < price <= 19: price_score = 60
                
                # Calculate metaphysics score (5%)
                metaphysics_score = 50
                last_digits = code[-3:]
                if '8' in last_digits or '6' in last_digits:
                    metaphysics_score = 70
                elif '4' in last_digits:
                    metaphysics_score = 30
                
                # Weighted total score
                total_score = (
                    technical_score * WEIGHTS["technical"] / 100 +
                    fundamental_score * WEIGHTS["fundamental"] / 100 +
                    policy_score * WEIGHTS["policy"] / 100 +
                    volume_score * WEIGHTS["volume"] / 100 +
                    price_score * WEIGHTS["price"] / 100 +
                    metaphysics_score * WEIGHTS["metaphysics"] / 100
                )
                
                # Calculate holding recommendation
                holding = _calculate_holding_recommendation(
                    change_1d, change_5d, change_10d, turn, roe, price
                )
                
                # Determine risk level
                if change_5d > 15:
                    risk = "高"
                elif change_5d > 8:
                    risk = "中高"
                elif change_5d > 0:
                    risk = "中等"
                else:
                    risk = "低"
                
                candidates.append({
                    'code': code.split('.')[1],
                    'name': name,
                    'price': price,
                    'cost_100': cost_100,
                    'change_1d': round(change_1d, 2),
                    'change_5d': round(change_5d, 2),
                    'change_10d': round(change_10d, 2),
                    'turnover': turn,
                    'technical_score': round(technical_score, 1),
                    'fundamental_score': round(fundamental_score, 1),
                    'policy_score': round(policy_score, 1),
                    'volume_score': round(volume_score, 1),
                    'price_score': round(price_score, 1),
                    'metaphysics_score': round(metaphysics_score, 1),
                    'total_score': round(total_score, 1),
                    'holding': holding,
                    'risk': risk,
                    'roe': round(roe, 2),
                    'gp_margin': round(gp_margin, 2),
                })
                
            except Exception:
                continue
        
        bs.logout()
        
        # Sort by total score
        candidates.sort(key=lambda x: -x['total_score'])
        
        logger.info(f"Found {len(candidates)} stocks, returning top {top_n}")
        return candidates[:top_n]
        
    except Exception as e:
        logger.error(f"Comprehensive scoring failed: {e}")
        return []


def format_top_stocks_report(stocks: List[Dict[str, Any]], budget: float = 1800) -> str:
    """Format top stocks as readable report."""
    lines = [
        "=" * 70,
        "综合评分TOP10 - 激进偏保守策略",
        f"预算: {budget}元 | 券商: 金元证券",
        "=" * 70,
        "",
        "评分权重:",
        "  技术面: 25% | 基本面: 25% | 政策面: 20%",
        "  流动性: 15% | 价格位: 10% | 玄学: 5%",
        "",
    ]
    
    for i, s in enumerate(stocks, 1):
        lines.extend([
            f"【第{i}名】{s['name']} ({s['code']})",
            f"  当前价格: {s['price']:.2f}元 | 1手成本: {s['cost_100']:.0f}元",
            f"  涨跌幅: {s['change_1d']:+.2f}%",
            f"  换手率: {s['turnover']:.2f}%",
            "",
            f"  综合评分: {s['total_score']}/100",
            f"    技术面(25%): {s['technical_score']}",
            f"    基本面(25%): {s['fundamental_score']}",
            f"    政策面(20%): {s['policy_score']}",
            f"    流动性(15%): {s['volume_score']}",
            f"    价格位(10%): {s['price_score']}",
            f"    玄学(5%): {s['metaphysics_score']}",
            "",
            f"  建议持仓: {s['holding']['period']}",
            f"  持仓策略: {s['holding']['reason']}",
            f"  风险等级: {s['risk']}",
            "",
        ])
    
    return "\n".join(lines)


if __name__ == "__main__":
    stocks = get_comprehensive_top_stocks(budget=1800, top_n=10)
    print(format_top_stocks_report(stocks, budget=1800))
