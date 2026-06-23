"""Investment learning-based strategy analyzer.

Based on the investment learning roadmap:
- Phase 1: Build correct investment worldview
- Phase 2: Learn financial statement analysis
- Phase 3: Build circle of competence
- Phase 4: Valuation and trading system
- Phase 5: Macro understanding

Strategy style: Aggressive but conservative (激进偏保守)
- Aggressive: Look for high-growth opportunities
- Conservative: Strict risk management, don't chase highs
"""

from typing import Dict, List, Any
from loguru import logger


class LearningBasedStrategy:
    """Strategy based on investment learning principles."""
    
    # Investment principles from the roadmap
    PRINCIPLES = {
        "safety_margin": "安全边际 - 买入价格要低于内在价值",
        "circle_of_competence": "能力圈 - 只投资自己理解的企业",
        "moat": "护城河 - 寻找有竞争优势的企业",
        "long_term": "长期主义 - 关注企业长期价值，忽略短期波动",
        "risk_management": "风险管理 - 单只不超过40%，严格止损",
    }
    
    # Quality checklist for stock selection
    QUALITY_CHECKLIST = {
        "financial_health": {
            "description": "财务健康度",
            "checks": [
                "资产负债率 < 60%",
                "经营现金流为正",
                "货币资金充足",
                "商誉占比低",
            ]
        },
        "profitability": {
            "description": "盈利能力",
            "checks": [
                "毛利率 > 30%",
                "净利率 > 10%",
                "ROE > 15%",
                "营收稳定增长",
            ]
        },
        "valuation": {
            "description": "估值合理性",
            "checks": [
                "PE < 行业平均",
                "PB < 3",
                "股息率 > 2%",
                "PEG < 1",
            ]
        },
        "moat": {
            "description": "护城河",
            "checks": [
                "品牌优势",
                "成本优势",
                "网络效应",
                "牌照壁垒",
                "技术壁垒",
            ]
        }
    }
    
    def evaluate_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a stock based on learning principles.
        
        Args:
            stock_data: Stock data dictionary
            
        Returns:
            Evaluation result with score and recommendation
        """
        score = 50  # Base score
        reasons = []
        risks = []
        
        # Price factor (for small capital)
        price = stock_data.get('price', 0)
        if 5 <= price <= 15:
            score += 10
            reasons.append("价格适中，适合小资金")
        elif price > 20:
            score -= 10
            risks.append("价格偏高，1手成本大")
        
        # Trend factor
        change = stock_data.get('change', 0)
        if 0 < change <= 5:
            score += 5
            reasons.append("温和上涨")
        elif change > 10:
            score -= 5
            risks.append("涨幅过大，追高风险")
        
        # PE factor (valuation)
        pe = stock_data.get('pe')
        if pe and 0 < pe < 30:
            score += 10
            reasons.append("估值合理")
        elif pe and pe > 50:
            score -= 10
            risks.append("估值偏高")
        
        # Volume factor (liquidity)
        volume = stock_data.get('volume', 0)
        if volume > 1000000:
            score += 5
            reasons.append("流动性好")
        
        # Generate recommendation
        if score >= 70:
            recommendation = "推荐买入"
            action = "buy"
        elif score >= 60:
            recommendation = "可以关注"
            action = "watch"
        elif score >= 50:
            recommendation = "观望"
            action = "hold"
        else:
            recommendation = "不建议买入"
            action = "avoid"
        
        return {
            "code": stock_data.get('code', ''),
            "name": stock_data.get('name', ''),
            "score": score,
            "recommendation": recommendation,
            "action": action,
            "reasons": reasons,
            "risks": risks,
            "principles_applied": self._get_applied_principles(stock_data)
        }
    
    def _get_applied_principles(self, stock_data: Dict) -> List[str]:
        """Get which investment principles are relevant."""
        applied = []
        
        # Safety margin
        pe = stock_data.get('pe')
        if pe and 0 < pe < 25:
            applied.append("安全边际: 估值较低")
        
        # Risk management
        price = stock_data.get('price', 0)
        if price < 15:
            applied.append("风险管理: 低价股，1手成本可控")
        
        return applied
    
    def generate_learning_based_plan(self, stocks: List[Dict], 
                                      capital: float = 1800) -> Dict[str, Any]:
        """Generate investment plan based on learning principles.
        
        Args:
            stocks: List of stock data
            capital: Available capital
            
        Returns:
            Investment plan
        """
        # Evaluate each stock
        evaluated = []
        for stock in stocks:
            result = self.evaluate_stock(stock)
            if result['action'] in ['buy', 'watch']:
                evaluated.append({**stock, **result})
        
        # Sort by score
        evaluated.sort(key=lambda x: -x['score'])
        
        # Generate plan
        plan = {
            "capital": capital,
            "style": "激进偏保守",
            "principles": [
                "严格止损: -5%止损",
                "分散投资: 单只不超过40%",
                "估值优先: PE<30优先",
                "流动性: 选成交量大的股票",
            ],
            "recommendations": [],
            "risk_management": {
                "max_single_position": capital * 0.4,
                "stop_loss_pct": 0.05,
                "take_profit_pct": 0.10,
                "max_holdings": 3,
            }
        }
        
        # Select top stocks
        remaining = capital
        for stock in evaluated[:3]:
            price = stock.get('price', 0)
            cost_100 = price * 100
            
            if cost_100 <= remaining * 0.4:  # Max 40% per position
                plan["recommendations"].append({
                    "code": stock['code'],
                    "name": stock['name'],
                    "price": price,
                    "score": stock['score'],
                    "reason": stock['recommendation'],
                    "max_buy": min(100, int(remaining * 0.4 / price / 100) * 100),
                    "stop_loss": round(price * 0.95, 2),
                    "take_profit": round(price * 1.10, 2),
                })
                remaining -= cost_100
        
        return plan


def format_learning_advice(stock_data: Dict) -> str:
    """Format learning-based advice for a stock."""
    strategy = LearningBasedStrategy()
    result = strategy.evaluate_stock(stock_data)
    
    lines = [
        "=" * 50,
        f"学习型分析: {result['name']} ({result['code']})",
        "=" * 50,
        f"综合评分: {result['score']}/100",
        f"建议: {result['recommendation']}",
        "",
        "优势:",
    ]
    
    for r in result['reasons']:
        lines.append(f"  + {r}")
    
    lines.append("\n风险:")
    for r in result['risks']:
        lines.append(f"  - {r}")
    
    lines.append("\n应用的投资原则:")
    for p in result['principles_applied']:
        lines.append(f"  * {p}")
    
    return "\n".join(lines)
