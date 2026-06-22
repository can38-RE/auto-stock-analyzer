"""Value investing analyzer based on Buffett/Munger philosophy.

Analyzes stocks using ROIC (Return on Invested Capital) and Earnings Yield
to categorize stocks into four tiers and provide buy recommendations.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from loguru import logger


class StockTier(Enum):
    """Stock quality tiers based on value investing principles."""
    TIER_1 = "A级 - 优质标的"  # High ROIC, High Earnings Yield
    TIER_2 = "B级 - 良好标的"  # High ROIC or High Earnings Yield
    TIER_3 = "C级 - 一般标的"  # Average metrics
    TIER_4 = "D级 - 观望标的"  # Below average metrics


@dataclass
class ValueAnalysisResult:
    """Value analysis result for a stock."""
    code: str
    name: str
    roic: float  # Return on Invested Capital (%)
    earnings_yield: float  # Earnings Yield (%)
    pe_ratio: float
    pb_ratio: float
    roe: float  # Return on Equity (%)
    debt_ratio: float  # Debt to Asset Ratio (%)
    tier: StockTier
    buy_recommendation: str
    intrinsic_value_range: str
    margin_of_safety: float  # Margin of Safety (%)
    key_strengths: List[str]
    key_risks: List[str]
    summary: str


class ValueInvestingAnalyzer:
    """Analyze stocks using Buffett/Munger value investing principles.
    
    Key metrics:
    - ROIC (Return on Invested Capital): Measures how efficiently a company uses capital
    - Earnings Yield: Earnings/Price, inverse of PE ratio
    - Margin of Safety: Discount to intrinsic value
    
    Tier Classification:
    - Tier 1 (A级): ROIC > 15% AND Earnings Yield > 5%
    - Tier 2 (B级): ROIC > 10% OR Earnings Yield > 4%
    - Tier 3 (C级): ROIC > 5% AND Earnings Yield > 2%
    - Tier 4 (D级): Below Tier 3 thresholds
    """
    
    # Thresholds for tier classification
    TIER_1_ROIC = 15.0  # %
    TIER_1_EY = 5.0     # %
    TIER_2_ROIC = 10.0  # %
    TIER_2_EY = 4.0     # %
    TIER_3_ROIC = 5.0   # %
    TIER_3_EY = 2.0     # %
    
    # Ideal ranges for value investing
    IDEAL_PE_RANGE = (5, 25)
    IDEAL_PB_RANGE = (0.5, 5.0)
    IDEAL_ROE_MIN = 10.0  # %
    IDEAL_DEBT_MAX = 60.0  # %
    
    def analyze_stock(self, stock_data: Dict[str, Any]) -> Optional[ValueAnalysisResult]:
        """Analyze a single stock using value investing principles.
        
        Args:
            stock_data: Dictionary containing stock financial data
            
        Returns:
            ValueAnalysisResult or None if data insufficient
        """
        try:
            code = stock_data.get('code', '')
            name = stock_data.get('name', '')
            price = stock_data.get('price', 0)
            pe = stock_data.get('pe')
            pb = stock_data.get('pb')
            roe = stock_data.get('roe')
            
            # Skip if essential data missing
            if not price or not pe:
                return None
            
            # Calculate key metrics
            roic = self._calculate_roic(stock_data)
            earnings_yield = self._calculate_earnings_yield(pe)
            debt_ratio = stock_data.get('debt_ratio', 30.0)
            
            # Classify tier
            tier = self._classify_tier(roic, earnings_yield)
            
            # Calculate margin of safety
            margin_of_safety = self._calculate_margin_of_safety(price, pe, pb, roe)
            
            # Generate buy recommendation
            buy_recommendation = self._generate_recommendation(tier, margin_of_safety)
            
            # Estimate intrinsic value range
            intrinsic_value_range = self._estimate_intrinsic_value(price, pe, pb, roe)
            
            # Identify strengths and risks
            key_strengths = self._identify_strengths(roic, earnings_yield, roe, debt_ratio, pe, pb)
            key_risks = self._identify_risks(roic, earnings_yield, roe, debt_ratio, pe, pb)
            
            # Generate summary
            summary = self._generate_summary(tier, buy_recommendation, margin_of_safety, key_strengths)
            
            return ValueAnalysisResult(
                code=code,
                name=name,
                roic=round(roic, 2),
                earnings_yield=round(earnings_yield, 2),
                pe_ratio=pe,
                pb_ratio=pb or 0,
                roe=roe or 0,
                debt_ratio=debt_ratio,
                tier=tier,
                buy_recommendation=buy_recommendation,
                intrinsic_value_range=intrinsic_value_range,
                margin_of_safety=round(margin_of_safety, 2),
                key_strengths=key_strengths,
                key_risks=key_risks,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze stock {stock_data.get('code', 'unknown')}: {e}")
            return None
    
    def analyze_multiple(self, stocks: List[Dict[str, Any]], top_n: int = 20) -> List[ValueAnalysisResult]:
        """Analyze multiple stocks and return top N by value score.
        
        Args:
            stocks: List of stock data dictionaries
            top_n: Number of top stocks to return
            
        Returns:
            List of ValueAnalysisResult sorted by tier and margin of safety
        """
        results = []
        
        for stock in stocks:
            result = self.analyze_stock(stock)
            if result:
                results.append(result)
        
        # Sort by tier (ascending) then by margin of safety (descending)
        tier_order = {
            StockTier.TIER_1: 0,
            StockTier.TIER_2: 1,
            StockTier.TIER_3: 2,
            StockTier.TIER_4: 3
        }
        
        results.sort(key=lambda x: (tier_order[x.tier], -x.margin_of_safety))
        
        return results[:top_n]
    
    def _calculate_roic(self, stock_data: Dict[str, Any]) -> float:
        """Calculate Return on Invested Capital (ROIC).
        
        ROIC = NOPAT / Invested Capital
        
        Simplified: ROIC ≈ ROE * (1 - Debt Ratio / 100)
        """
        roe = stock_data.get('roe', 10.0) or 10.0
        debt_ratio = stock_data.get('debt_ratio', 30.0) or 30.0
        
        # Simplified ROIC calculation
        roic = roe * (1 - debt_ratio / 100)
        
        return max(roic, 0)
    
    def _calculate_earnings_yield(self, pe: float) -> float:
        """Calculate Earnings Yield.
        
        Earnings Yield = 1 / PE * 100
        """
        if pe and pe > 0:
            return (1 / pe) * 100
        return 0
    
    def _classify_tier(self, roic: float, earnings_yield: float) -> StockTier:
        """Classify stock into tier based on ROIC and Earnings Yield."""
        if roic >= self.TIER_1_ROIC and earnings_yield >= self.TIER_1_EY:
            return StockTier.TIER_1
        elif roic >= self.TIER_2_ROIC or earnings_yield >= self.TIER_2_EY:
            return StockTier.TIER_2
        elif roic >= self.TIER_3_ROIC and earnings_yield >= self.TIER_3_EY:
            return StockTier.TIER_3
        else:
            return StockTier.TIER_4
    
    def _calculate_margin_of_safety(self, price: float, pe: float, pb: float, roe: float) -> float:
        """Calculate Margin of Safety.
        
        Margin of Safety = (Intrinsic Value - Market Price) / Intrinsic Value * 100
        
        Simplified: Based on PE and PB relative to growth
        """
        if not pe or pe <= 0:
            return 0
        
        # Fair PE based on ROE
        fair_pe = roe * 1.5 if roe else 15
        
        # Calculate intrinsic value
        intrinsic_value = price * (fair_pe / pe)
        
        # Margin of safety
        if intrinsic_value > 0:
            margin = ((intrinsic_value - price) / intrinsic_value) * 100
            return max(min(margin, 80), -50)  # Cap between -50% and 80%
        
        return 0
    
    def _estimate_intrinsic_value(self, price: float, pe: float, pb: float, roe: float) -> str:
        """Estimate intrinsic value range."""
        if not pe or pe <= 0:
            return "无法估算"
        
        # Fair PE based on ROE
        fair_pe = roe * 1.5 if roe else 15
        
        # Calculate range
        low = price * (fair_pe * 0.7 / pe)
        high = price * (fair_pe * 1.3 / pe)
        
        return f"¥{low:.2f} - ¥{high:.2f}"
    
    def _generate_recommendation(self, tier: StockTier, margin_of_safety: float) -> str:
        """Generate buy recommendation based on tier and margin of safety."""
        if tier == StockTier.TIER_1:
            if margin_of_safety > 30:
                return "强烈推荐买入"
            elif margin_of_safety > 15:
                return "推荐买入"
            else:
                return "建议买入"
        elif tier == StockTier.TIER_2:
            if margin_of_safety > 20:
                return "推荐买入"
            elif margin_of_safety > 10:
                return "建议买入"
            else:
                return "观望等待更好价格"
        elif tier == StockTier.TIER_3:
            if margin_of_safety > 25:
                return "谨慎买入"
            else:
                return "观望"
        else:
            return "不建议买入"
    
    def _identify_strengths(self, roic: float, ey: float, roe: float, 
                           debt: float, pe: float, pb: float) -> List[str]:
        """Identify key strengths of the stock."""
        strengths = []
        
        if roic >= 15:
            strengths.append(f"ROIC优秀({roic:.1f}%)，资本运用效率高")
        elif roic >= 10:
            strengths.append(f"ROIC良好({roic:.1f}%)")
        
        if ey >= 5:
            strengths.append(f"盈利收益率高({ey:.1f}%)，估值有吸引力")
        elif ey >= 4:
            strengths.append(f"盈利收益率良好({ey:.1f}%)")
        
        if roe and roe >= 15:
            strengths.append(f"ROE优秀({roe:.1f}%)，盈利能力强")
        elif roe and roe >= 10:
            strengths.append(f"ROE良好({roe:.1f}%)")
        
        if debt and debt < 40:
            strengths.append(f"负债率低({debt:.1f}%)，财务稳健")
        
        if pe and 5 <= pe <= 15:
            strengths.append(f"PE估值合理({pe:.1f})")
        
        if not strengths:
            strengths.append("暂无明显优势")
        
        return strengths
    
    def _identify_risks(self, roic: float, ey: float, roe: float,
                       debt: float, pe: float, pb: float) -> List[str]:
        """Identify key risks of the stock."""
        risks = []
        
        if roic < 5:
            risks.append(f"ROIC偏低({roic:.1f}%)，资本运用效率不足")
        
        if ey < 2:
            risks.append(f"盈利收益率低({ey:.1f}%)，估值偏高")
        
        if roe and roe < 5:
            risks.append(f"ROE偏低({roe:.1f}%)，盈利能力弱")
        
        if debt and debt > 70:
            risks.append(f"负债率高({debt:.1f}%)，财务风险较大")
        
        if pe and pe > 50:
            risks.append(f"PE估值过高({pe:.1f})，存在泡沫风险")
        elif pe and pe < 0:
            risks.append("公司亏损，基本面恶化")
        
        if not risks:
            risks.append("暂无明显风险")
        
        return risks
    
    def _generate_summary(self, tier: StockTier, recommendation: str,
                         margin_of_safety: float, strengths: List[str]) -> str:
        """Generate analysis summary."""
        tier_desc = tier.value.split(' - ')[1] if ' - ' in tier.value else tier.value
        
        summary = f"【{tier_desc}】{recommendation}"
        
        if margin_of_safety > 20:
            summary += f"，安全边际充足({margin_of_safety:.1f}%)"
        elif margin_of_safety > 0:
            summary += f"，有一定安全边际({margin_of_safety:.1f}%)"
        else:
            summary += f"，安全边际不足({margin_of_safety:.1f}%)"
        
        if strengths and strengths[0] != "暂无明显优势":
            summary += f"。核心优势：{strengths[0]}"
        
        return summary


def format_value_analysis(result: ValueAnalysisResult) -> str:
    """Format value analysis result as readable text."""
    lines = [
        f"{'='*50}",
        f"📊 价值投资分析报告 - {result.name} ({result.code})",
        f"{'='*50}",
        "",
        f"🏆 评级: {result.tier.value}",
        f"💡 建议: {result.buy_recommendation}",
        "",
        "📈 核心指标:",
        f"  • ROIC (投资资本回报率): {result.roic}%",
        f"  • 盈利收益率: {result.earnings_yield}%",
        f"  • PE (市盈率): {result.pe_ratio:.1f}",
        f"  • PB (市净率): {result.pb_ratio:.1f}",
        f"  • ROE (净资产收益率): {result.roe:.1f}%",
        f"  • 负债率: {result.debt_ratio:.1f}%",
        "",
        f"💰 内在价值区间: {result.intrinsic_value_range}",
        f"🛡️ 安全边际: {result.margin_of_safety}%",
        "",
        "✅ 核心优势:",
    ]
    
    for s in result.key_strengths:
        lines.append(f"  • {s}")
    
    lines.append("")
    lines.append("⚠️ 主要风险:")
    for r in result.key_risks:
        lines.append(f"  • {r}")
    
    lines.append("")
    lines.append(f"📝 总结: {result.summary}")
    lines.append(f"{'='*50}")
    
    return "\n".join(lines)
