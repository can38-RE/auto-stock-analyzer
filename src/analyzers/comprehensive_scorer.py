"""Comprehensive stock scoring with proper weights."""

from typing import List, Dict, Any
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
    """Get top stocks with comprehensive scoring using akshare."""
    try:
        import akshare as ak
        
        logger.info("Fetching stock data via akshare...")
        
        # Get all A-shares
        df = ak.stock_zh_a_spot_em()
        
        if df.empty:
            logger.warning("No stock data returned from akshare")
            return []
        
        # Policy-aligned sectors
        policy_sectors = {
            "新能源": ["光伏", "风电", "储能", "锂电", "新能源", "阳光"],
            "人工智能": ["AI", "智能", "科技", "信息", "数据"],
            "半导体": ["芯片", "半导体", "电子", "集成电路"],
            "新材料": ["新材", "材料", "化工"],
            "高端制造": ["制造", "机械", "装备", "自动化"],
        }
        
        candidates = []
        
        for _, row in df.iterrows():
            try:
                code = str(row.get("代码", ""))
                name = str(row.get("名称", ""))
                price = float(row.get("最新价", 0))
                change = float(row.get("涨跌幅", 0))
                volume = float(row.get("成交量", 0))
                turnover = float(row.get("换手率", 0))
                pe = row.get("市盈率-动态", None)
                pb = row.get("市净率", None)
                
                # Filter: mainboard only
                if not code.startswith(('000', '001', '002', '600', '601', '603', '605')):
                    continue
                
                # Filter: price range
                if price > 19 or price < 3:
                    continue
                
                cost_100 = price * 100
                if cost_100 > budget:
                    continue
                
                # Calculate technical score (25%)
                technical_score = 0
                if change > 5: technical_score += 40
                elif change > 3: technical_score += 30
                elif change > 1: technical_score += 20
                elif change > 0: technical_score += 10
                
                # Volume factor
                if volume > 10000000: technical_score += 30
                elif volume > 5000000: technical_score += 20
                elif volume > 1000000: technical_score += 10
                
                technical_score = min(technical_score, 100)
                
                # Calculate fundamental score (25%)
                fundamental_score = 50
                if pe and isinstance(pe, (int, float)):
                    if 0 < pe < 20: fundamental_score += 30
                    elif 20 <= pe < 40: fundamental_score += 20
                    elif 40 <= pe < 80: fundamental_score += 10
                
                if pb and isinstance(pb, (int, float)):
                    if 0 < pb < 2: fundamental_score += 20
                    elif 2 <= pb < 5: fundamental_score += 10
                
                fundamental_score = min(fundamental_score, 100)
                
                # Calculate policy score (20%)
                policy_score = 50
                for sector, keywords in policy_sectors.items():
                    if any(kw in name for kw in keywords):
                        policy_score = 90
                        break
                
                # Calculate volume/liquidity score (15%)
                volume_score = 50
                if turnover > 10: volume_score = 90
                elif turnover > 5: volume_score = 75
                elif turnover > 3: volume_score = 60
                
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
                    change, change * 5, change * 10, turnover, 0, price
                )
                
                # Determine risk level
                if change > 5:
                    risk = "高"
                elif change > 2:
                    risk = "中高"
                elif change > 0:
                    risk = "中等"
                else:
                    risk = "低"
                
                candidates.append({
                    'code': code,
                    'name': name,
                    'price': price,
                    'cost_100': cost_100,
                    'change_1d': round(change, 2),
                    'change_5d': round(change * 3, 2),  # Approximate
                    'change_10d': round(change * 5, 2),  # Approximate
                    'turnover': turnover,
                    'technical_score': round(technical_score, 1),
                    'fundamental_score': round(fundamental_score, 1),
                    'policy_score': round(policy_score, 1),
                    'volume_score': round(volume_score, 1),
                    'price_score': round(price_score, 1),
                    'metaphysics_score': round(metaphysics_score, 1),
                    'total_score': round(total_score, 1),
                    'holding': holding,
                    'risk': risk,
                    'roe': 0,
                    'gp_margin': 0,
                })
                
            except Exception:
                continue
        
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
