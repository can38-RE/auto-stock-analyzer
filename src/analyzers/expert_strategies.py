"""专家投资策略分析模块。

整合国内外知名投资大师的选股哲学与量化评分体系，包括：
- 国际：巴菲特、芒格、林奇、格雷厄姆、霍华德·马克斯
- 国内：但斌、林园、段永平、张磊、邱国鹭

每套策略独立评分，最终汇总为综合专家推荐。
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger


class ExpertVerdict(Enum):
    """专家评级。"""
    STRONG_BUY = "强烈推荐"
    BUY = "推荐买入"
    HOLD = "持有观望"
    AVOID = "不建议买入"


@dataclass
class ExpertScore:
    """单个专家对某只股票的评分结果。"""
    expert_name: str
    philosophy: str
    score: float  # 0-100
    verdict: ExpertVerdict
    reasoning: List[str]
    key_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExpertAnalysisResult:
    """综合专家分析结果。"""
    code: str
    name: str
    expert_scores: List[ExpertScore]
    composite_score: float  # 加权综合分
    composite_verdict: ExpertVerdict
    top_reasons: List[str]
    consensus_summary: str


# ---------------------------------------------------------------------------
# 国际大师策略
# ---------------------------------------------------------------------------

class BuffettStrategy:
    """沃伦·巴菲特 —— 价值投资、护城河理论、长期持有。

    核心思想：
    1. 以合理价格买入优秀公司，而非以便宜价格买入平庸公司
    2. 关注护城河（品牌、成本优势、网络效应、转换成本）
    3. 长期持有，复利增长
    4. 只投自己看得懂的生意（能力圈）
    """

    NAME = "沃伦·巴菲特"
    PHILOSOPHY = "价值投资 · 护城河理论 · 长期持有"

    def score(self, data: Dict[str, Any]) -> ExpertScore:
        s = 0.0
        reasons: List[str] = []

        roe = data.get("roe") or 0
        pe = data.get("pe") or 0
        pb = data.get("pb") or 0
        debt = data.get("debt_ratio") or 50
        revenue_growth = data.get("revenue_growth") or 0
        dividend_yield = data.get("dividend_yield") or 0

        # ROE 连续优秀
        if roe >= 20:
            s += 25
            reasons.append(f"ROE高达{roe:.1f}%，盈利能力卓越")
        elif roe >= 15:
            s += 18
            reasons.append(f"ROE为{roe:.1f}%，盈利能力优秀")
        elif roe >= 10:
            s += 10
            reasons.append(f"ROE为{roe:.1f}%，盈利能力尚可")
        else:
            reasons.append(f"ROE仅{roe:.1f}%，盈利能力偏弱")

        # 估值合理
        if 0 < pe <= 15:
            s += 20
            reasons.append(f"PE仅{pe:.1f}，估值极具吸引力")
        elif 15 < pe <= 25:
            s += 12
            reasons.append(f"PE为{pe:.1f}，估值合理")
        elif 25 < pe <= 40:
            s += 5
            reasons.append(f"PE为{pe:.1f}，估值偏高")
        elif pe > 40:
            reasons.append(f"PE高达{pe:.1f}，估值过高")

        # 负债率低
        if debt < 30:
            s += 15
            reasons.append(f"负债率仅{debt:.1f}%，财务非常稳健")
        elif debt < 50:
            s += 8
            reasons.append(f"负债率{debt:.1f}%，财务较稳健")
        elif debt >= 70:
            reasons.append(f"负债率{debt:.1f}%，财务风险较高")

        # 营收增长（持续成长性）
        if revenue_growth >= 15:
            s += 15
            reasons.append(f"营收增长{revenue_growth:.1f}%，成长性突出")
        elif revenue_growth >= 8:
            s += 10
            reasons.append(f"营收增长{revenue_growth:.1f}%，稳步增长")
        elif revenue_growth > 0:
            s += 5

        # 分红（巴菲特喜欢现金流回馈）
        if dividend_yield >= 3:
            s += 10
            reasons.append(f"股息率{dividend_yield:.1f}%，股东回报优秀")
        elif dividend_yield >= 1.5:
            s += 5

        # PB 合理
        if 0 < pb <= 3:
            s += 10
        elif 3 < pb <= 6:
            s += 5

        verdict = self._verdict(s)
        return ExpertScore(
            expert_name=self.NAME,
            philosophy=self.PHILOSOPHY,
            score=min(s, 100),
            verdict=verdict,
            reasoning=reasons,
        )

    @staticmethod
    def _verdict(s: float) -> ExpertVerdict:
        if s >= 70:
            return ExpertVerdict.STRONG_BUY
        if s >= 50:
            return ExpertVerdict.BUY
        if s >= 30:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID


class MungerStrategy:
    """查理·芒格 —— 多元思维模型、逆向思维、理性决策。

    核心思想：
    1. 跨学科多元思维模型（心理学、物理学、生物学等）
    2. 逆向思考：先想如何失败，再避免之
    3. 好公司 + 好管理层 + 好价格
    4. 减少决策频率，提高决策质量
    """

    NAME = "查理·芒格"
    PHILOSOPHY = "多元思维模型 · 逆向思维 · 理性决策"

    def score(self, data: Dict[str, Any]) -> ExpertScore:
        s = 0.0
        reasons: List[str] = []

        roe = data.get("roe") or 0
        pe = data.get("pe") or 0
        debt = data.get("debt_ratio") or 50
        gross_margin = data.get("gross_margin") or 0
        net_margin = data.get("net_margin") or 0
        roic = data.get("roic") or (roe * (1 - debt / 100) if roe else 0)

        # 资本回报率（芒格最看重）
        if roic >= 15:
            s += 25
            reasons.append(f"ROIC为{roic:.1f}%，经济特许权突出")
        elif roic >= 10:
            s += 15
            reasons.append(f"ROIC为{roic:.1f}%，资本回报良好")

        # 毛利率体现定价权
        if gross_margin >= 50:
            s += 20
            reasons.append(f"毛利率{gross_margin:.1f}%，拥有强大定价权")
        elif gross_margin >= 30:
            s += 10
            reasons.append(f"毛利率{gross_margin:.1f}%，盈利能力尚可")

        # 净利率
        if net_margin >= 20:
            s += 15
            reasons.append(f"净利率{net_margin:.1f}%，经营效率极高")
        elif net_margin >= 10:
            s += 8

        # 财务保守（芒格厌恶高杠杆）
        if debt < 25:
            s += 15
            reasons.append(f"负债率仅{debt:.1f}%，极度保守稳健")
        elif debt < 45:
            s += 8
        elif debt >= 65:
            reasons.append(f"负债率{debt:.1f}%，芒格会避开此类公司")

        # 估值理性
        if 0 < pe <= 20:
            s += 15
            reasons.append(f"PE为{pe:.1f}，价格合理")
        elif 20 < pe <= 35:
            s += 5
        elif pe > 50:
            reasons.append("估值过高，不符合芒格理性投资原则")

        # ROE
        if roe >= 15:
            s += 10

        verdict = self._verdict(s)
        return ExpertScore(
            expert_name=self.NAME,
            philosophy=self.PHILOSOPHY,
            score=min(s, 100),
            verdict=verdict,
            reasoning=reasons,
        )

    @staticmethod
    def _verdict(s: float) -> ExpertVerdict:
        if s >= 65:
            return ExpertVerdict.STRONG_BUY
        if s >= 45:
            return ExpertVerdict.BUY
        if s >= 25:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID


class LynchStrategy:
    """彼得·林奇 —— GARP策略、股票分类、实地调研。

    核心思想：
    1. Growth at a Reasonable Price (GARP)：PEG < 1 为佳
    2. 将股票分为六类：慢速增长、稳定增长、快速增长、周期股、资产隐蔽型、困境反转型
    3. 从生活中发现牛股（"十倍股"）
    4. 不碰自己不懂的行业
    """

    NAME = "彼得·林奇"
    PHILOSOPHY = "GARP策略 · 股票六分类 · 十倍股挖掘"

    STOCK_CATEGORIES = {
        "slow_grower": "慢速增长型",
        "stalwart": "稳定增长型",
        "fast_grower": "快速增长型",
        "cyclical": "周期型",
        "turnaround": "困境反转型",
        "asset_play": "资产隐蔽型",
    }

    def score(self, data: Dict[str, Any]) -> ExpertScore:
        s = 0.0
        reasons: List[str] = []

        pe = data.get("pe") or 0
        roe = data.get("roe") or 0
        revenue_growth = data.get("revenue_growth") or 0
        earnings_growth = data.get("earnings_growth") or data.get("revenue_growth") or 0
        debt = data.get("debt_ratio") or 50
        pb = data.get("pb") or 0

        # PEG 估值（林奇核心指标）
        peg = pe / earnings_growth if earnings_growth > 0 else 999
        if 0 < peg <= 0.5:
            s += 30
            reasons.append(f"PEG仅{peg:.2f}，极度低估的成长股")
        elif 0.5 < peg <= 1.0:
            s += 25
            reasons.append(f"PEG为{peg:.2f}，成长价格比优秀")
        elif 1.0 < peg <= 1.5:
            s += 15
            reasons.append(f"PEG为{peg:.2f}，估值尚可接受")
        elif 1.5 < peg <= 2.0:
            s += 5
            reasons.append(f"PEG为{peg:.2f}，估值偏高")
        elif peg > 2:
            reasons.append(f"PEG高达{peg:.2f}，成长性不足以支撑估值")

        # 股票分类
        category = self._categorize(data)
        reasons.append(f"林奇分类：{self.STOCK_CATEGORIES.get(category, '未知')}")
        if category == "fast_grower":
            s += 15
        elif category == "stalwart":
            s += 10
        elif category == "turnaround":
            s += 12
        elif category == "slow_grower":
            s += 3

        # 营收增长
        if revenue_growth >= 25:
            s += 15
            reasons.append(f"营收增长{revenue_growth:.1f}%，快速增长")
        elif revenue_growth >= 10:
            s += 10
            reasons.append(f"营收增长{revenue_growth:.1f}%，稳健增长")

        # 负债（林奇偏爱低负债）
        if debt < 30:
            s += 10
            reasons.append(f"负债率{debt:.1f}%，财务安全")
        elif debt >= 60:
            reasons.append(f"负债率{debt:.1f}%，需警惕债务风险")

        # ROE
        if roe >= 15:
            s += 10
        elif roe >= 10:
            s += 5

        # PB 合理性
        if 0 < pb <= 2:
            s += 5

        verdict = self._verdict(s)
        return ExpertScore(
            expert_name=self.NAME,
            philosophy=self.PHILOSOPHY,
            score=min(s, 100),
            verdict=verdict,
            reasoning=reasons,
            key_metrics={"peg": round(peg, 2), "category": self.STOCK_CATEGORIES.get(category, "未知")},
        )

    def _categorize(self, data: Dict[str, Any]) -> str:
        """林奇式股票分类。"""
        growth = data.get("revenue_growth") or 0
        pe = data.get("pe") or 0
        pb = data.get("pb") or 0
        debt = data.get("debt_ratio") or 50

        if growth >= 25:
            return "fast_grower"
        if growth >= 8 and pe < 25:
            return "stalwart"
        if 0 < growth <= 5:
            return "slow_grower"
        if pb > 0 and pb < 1:
            return "asset_play"
        if growth < 0 and data.get("roe", 0) > 0:
            return "turnaround"
        return "stalwart"

    @staticmethod
    def _verdict(s: float) -> ExpertVerdict:
        if s >= 70:
            return ExpertVerdict.STRONG_BUY
        if s >= 50:
            return ExpertVerdict.BUY
        if s >= 30:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID


class GrahamStrategy:
    """本杰明·格雷厄姆 —— 安全边际、防御型投资者、净净值法。

    核心思想：
    1. 安全边际：以远低于内在价值的价格买入
    2. 防御型投资者选股七原则（规模、财务、盈利稳定性、分红、增长、PE、PB）
    3. 净流动资产价值法（烟蒂股投资）
    4. 市场先生隐喻：市场短期是投票机，长期是称重机
    """

    NAME = "本杰明·格雷厄姆"
    PHILOSOPHY = "安全边际 · 防御型投资者 · 净净值法"

    def score(self, data: Dict[str, Any]) -> ExpertScore:
        s = 0.0
        reasons: List[str] = []

        pe = data.get("pe") or 0
        pb = data.get("pb") or 0
        roe = data.get("roe") or 0
        debt = data.get("debt_ratio") or 50
        dividend_yield = data.get("dividend_yield") or 0
        earnings_growth = data.get("earnings_growth") or data.get("revenue_growth") or 0
        current_ratio = data.get("current_ratio") or 2.0

        # Graham Number: sqrt(22.5 * EPS * BVPS)
        # 简化：PE * PB <= 22.5
        pe_pb_product = pe * pb if pe > 0 and pb > 0 else 999
        if pe_pb_product <= 22.5:
            s += 25
            reasons.append(f"PE×PB={pe_pb_product:.1f}≤22.5，符合格雷厄姆数字")
        elif pe_pb_product <= 40:
            s += 10
            reasons.append(f"PE×PB={pe_pb_product:.1f}，估值偏高但尚可")
        else:
            reasons.append(f"PE×PB={pe_pb_product:.1f}，估值过高")

        # PE 低估
        if 0 < pe <= 10:
            s += 20
            reasons.append(f"PE仅{pe:.1f}，极具安全边际")
        elif 10 < pe <= 15:
            s += 12
            reasons.append(f"PE为{pe:.1f}，估值偏低")
        elif 15 < pe <= 25:
            s += 5
        elif pe > 25:
            reasons.append(f"PE为{pe:.1f}，不满足格雷厄姆低估值要求")

        # PB 低估（格雷厄姆偏好 PB < 1.5）
        if 0 < pb <= 1.0:
            s += 15
            reasons.append(f"PB仅{pb:.2f}，低于账面价值")
        elif 1.0 < pb <= 1.5:
            s += 10
            reasons.append(f"PB为{pb:.2f}，接近账面价值")
        elif pb > 3:
            reasons.append(f"PB为{pb:.2f}，溢价过高")

        # 分红记录（防御型投资者要求连续20年分红）
        if dividend_yield >= 4:
            s += 15
            reasons.append(f"股息率{dividend_yield:.1f}%，分红丰厚")
        elif dividend_yield >= 2:
            s += 8
            reasons.append(f"股息率{dividend_yield:.1f}%，分红稳定")
        elif dividend_yield > 0:
            s += 3

        # 盈利稳定性（格雷厄姆要求过去10年无亏损）
        if earnings_growth >= 5:
            s += 10
            reasons.append(f"盈利增长{earnings_growth:.1f}%，符合持续盈利要求")

        # 流动比率（格雷厄姆要求 >= 2）
        if current_ratio >= 2:
            s += 8
            reasons.append(f"流动比率{current_ratio:.1f}，短期偿债能力强")
        elif current_ratio < 1:
            reasons.append(f"流动比率仅{current_ratio:.1f}，短期偿债能力不足")

        # 负债率（格雷厄姆要求长期负债 < 净流动资产）
        if debt < 40:
            s += 7
        elif debt >= 60:
            reasons.append(f"负债率{debt:.1f}%，财务杠杆过高")

        verdict = self._verdict(s)
        return ExpertScore(
            expert_name=self.NAME,
            philosophy=self.PHILOSOPHY,
            score=min(s, 100),
            verdict=verdict,
            reasoning=reasons,
            key_metrics={"pe_pb_product": round(pe_pb_product, 1)},
        )

    @staticmethod
    def _verdict(s: float) -> ExpertVerdict:
        if s >= 65:
            return ExpertVerdict.STRONG_BUY
        if s >= 45:
            return ExpertVerdict.BUY
        if s >= 25:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID


class HowardMarksStrategy:
    """霍华德·马克斯 —— 市场周期、风险控制、逆向投资。

    核心思想：
    1. 市场周期：在别人贪婪时恐惧，在别人恐惧时贪婪
    2. 风险不是波动，而是永久性资本损失的可能
    3. 第二层思维：比市场共识想得更深一层
    4. 关注价格与价值的关系，而非单纯的趋势
    """

    NAME = "霍华德·马克斯"
    PHILOSOPHY = "市场周期 · 风险管理 · 逆向投资"

    def score(self, data: Dict[str, Any]) -> ExpertScore:
        s = 0.0
        reasons: List[str] = []

        pe = data.get("pe") or 0
        pb = data.get("pb") or 0
        roe = data.get("roe") or 0
        debt = data.get("debt_ratio") or 50
        change_52w = data.get("change_52w") or 0  # 52周涨跌幅
        beta = data.get("beta") or 1.0

        # 价格与价值偏离度（逆向思维）
        if change_52w < -30:
            s += 20
            reasons.append(f"52周下跌{abs(change_52w):.1f}%，可能存在逆向机会")
        elif change_52w < -15:
            s += 15
            reasons.append(f"52周下跌{abs(change_52w):.1f}%，值得逆向关注")
        elif change_52w > 80:
            reasons.append(f"52周上涨{change_52w:.1f}%，风险正在积聚")

        # 低估值（马克斯强调买入价格）
        if 0 < pe <= 12:
            s += 20
            reasons.append(f"PE仅{pe:.1f}，价格远低于价值")
        elif 12 < pe <= 20:
            s += 10
        elif pe > 40:
            reasons.append(f"PE高达{pe:.1f}，价格远超价值")

        # PB 低估
        if 0 < pb <= 1.5:
            s += 15
            reasons.append(f"PB为{pb:.2f}，接近或低于账面价值")
        elif pb > 5:
            reasons.append(f"PB为{pb:.2f}，溢价过高")

        # 低风险（马克斯最看重风险控制）
        if debt < 30:
            s += 15
            reasons.append(f"负债率{debt:.1f}%，财务风险低")
        elif debt < 50:
            s += 8
        elif debt >= 70:
            reasons.append(f"负债率{debt:.1f}%，永久性损失风险高")

        # Beta（低波动 = 低风险）
        if beta < 0.8:
            s += 10
            reasons.append(f"Beta仅{beta:.2f}，防御性强")
        elif beta < 1.2:
            s += 5
        elif beta > 1.5:
            reasons.append(f"Beta为{beta:.2f}，波动风险较大")

        # ROE 稳健
        if roe >= 12:
            s += 10

        verdict = self._verdict(s)
        return ExpertScore(
            expert_name=self.NAME,
            philosophy=self.PHILOSOPHY,
            score=min(s, 100),
            verdict=verdict,
            reasoning=reasons,
        )

    @staticmethod
    def _verdict(s: float) -> ExpertVerdict:
        if s >= 65:
            return ExpertVerdict.STRONG_BUY
        if s >= 45:
            return ExpertVerdict.BUY
        if s >= 25:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID


# ---------------------------------------------------------------------------
# 国内大师策略
# ---------------------------------------------------------------------------

class DanBinStrategy:
    """但斌 —— 长期价值投资，白酒消费龙头。

    核心思想：
    1. 选择具有长期竞争优势的消费龙头，尤其白酒、食品饮料
    2. 时间的玫瑰：长期持有优质资产，享受复利增长
    3. 关注品牌壁垒和消费升级趋势
    4. 在市场恐慌时坚定持有甚至加仓
    """

    NAME = "但斌"
    PHILOSOPHY = "长期价值投资 · 白酒消费 · 时间的玫瑰"

    PREFERRED_SECTORS = ["白酒", "食品饮料", "消费品", "医药", "食品"]

    def score(self, data: Dict[str, Any]) -> ExpertScore:
        s = 0.0
        reasons: List[str] = []

        roe = data.get("roe") or 0
        pe = data.get("pe") or 0
        revenue_growth = data.get("revenue_growth") or 0
        net_margin = data.get("net_margin") or 0
        dividend_yield = data.get("dividend_yield") or 0
        sector = data.get("sector", "")

        # 行业偏好（白酒消费加分）
        if any(k in sector for k in self.PREFERRED_SECTORS):
            s += 20
            reasons.append(f"所属行业「{sector}」符合但斌核心持仓方向")
        elif "消费" in sector or "品牌" in data.get("name", ""):
            s += 10

        # ROE（但斌看重长期高ROE）
        if roe >= 20:
            s += 25
            reasons.append(f"ROE高达{roe:.1f}%，长期复利效应显著")
        elif roe >= 15:
            s += 18
            reasons.append(f"ROE为{roe:.1f}%，盈利能力优秀")
        elif roe >= 10:
            s += 10
        else:
            reasons.append(f"ROE仅{roe:.1f}%，不符合长期持有标准")

        # 净利率（品牌消费品通常高净利率）
        if net_margin >= 25:
            s += 15
            reasons.append(f"净利率{net_margin:.1f}%，品牌溢价能力极强")
        elif net_margin >= 15:
            s += 10
            reasons.append(f"净利率{net_margin:.1f}%，盈利能力良好")
        elif net_margin >= 8:
            s += 5

        # 营收稳定增长
        if revenue_growth >= 15:
            s += 15
            reasons.append(f"营收增长{revenue_growth:.1f}%，成长性突出")
        elif revenue_growth >= 8:
            s += 10
        elif revenue_growth > 0:
            s += 5

        # 估值（但斌可以接受较高PE给优质消费股）
        if 0 < pe <= 30:
            s += 10
        elif 30 < pe <= 50:
            s += 5
            reasons.append(f"PE为{pe:.1f}，对优质消费股尚可接受")
        elif pe > 60:
            reasons.append(f"PE高达{pe:.1f}，即使是好公司也需谨慎")

        # 分红
        if dividend_yield >= 2:
            s += 10
            reasons.append(f"股息率{dividend_yield:.1f}%，长期回报可观")

        verdict = self._verdict(s)
        return ExpertScore(
            expert_name=self.NAME,
            philosophy=self.PHILOSOPHY,
            score=min(s, 100),
            verdict=verdict,
            reasoning=reasons,
        )

    @staticmethod
    def _verdict(s: float) -> ExpertVerdict:
        if s >= 70:
            return ExpertVerdict.STRONG_BUY
        if s >= 50:
            return ExpertVerdict.BUY
        if s >= 30:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID


class LinYuanStrategy:
    """林园 —— 医药消费龙头，高ROE选股法。

    核心思想：
    1. 只投医药和消费两大黄金赛道
    2. 选择行业龙头，ROE必须长期 > 15%
    3. 市场需求确定性高（老龄化 + 消费升级）
    4. 不做波段，买入后长期持有
    """

    NAME = "林园"
    PHILOSOPHY = "医药消费龙头 · 高ROE选股 · 确定性增长"

    PREFERRED_SECTORS = ["医药", "医疗", "中药", "生物制品", "消费", "食品饮料", "白酒"]

    def score(self, data: Dict[str, Any]) -> ExpertScore:
        s = 0.0
        reasons: List[str] = []

        roe = data.get("roe") or 0
        pe = data.get("pe") or 0
        revenue_growth = data.get("revenue_growth") or 0
        net_margin = data.get("net_margin") or 0
        gross_margin = data.get("gross_margin") or 0
        sector = data.get("sector", "")

        # 行业筛选（林园只看医药消费）
        if any(k in sector for k in self.PREFERRED_SECTORS):
            s += 20
            reasons.append(f"行业「{sector}」属于林园核心赛道")
        else:
            reasons.append(f"行业「{sector}」不在林园核心关注范围")

        # ROE（林园选股第一标准）
        if roe >= 25:
            s += 30
            reasons.append(f"ROE高达{roe:.1f}%，远超林园15%标准线")
        elif roe >= 20:
            s += 25
            reasons.append(f"ROE为{roe:.1f}%，符合龙头标准")
        elif roe >= 15:
            s += 18
            reasons.append(f"ROE为{roe:.1f}%，满足林园选股底线")
        elif roe >= 10:
            s += 8
            reasons.append(f"ROE仅{roe:.1f}%，未达林园选股标准")
        else:
            reasons.append(f"ROE仅{roe:.1f}%，不满足林园选股要求")

        # 毛利率（定价权）
        if gross_margin >= 60:
            s += 12
            reasons.append(f"毛利率{gross_margin:.1f}%，具有极强定价权")
        elif gross_margin >= 40:
            s += 8
        elif gross_margin >= 25:
            s += 4

        # 净利率
        if net_margin >= 20:
            s += 10
            reasons.append(f"净利率{net_margin:.1f}%，盈利能力一流")
        elif net_margin >= 10:
            s += 5

        # 增长确定性
        if revenue_growth >= 15:
            s += 12
            reasons.append(f"营收增长{revenue_growth:.1f}%，确定性增长")
        elif revenue_growth >= 8:
            s += 6

        # 估值（林园对龙头容忍度较高）
        if 0 < pe <= 25:
            s += 8
        elif 25 < pe <= 45:
            s += 4
        elif pe > 50:
            reasons.append(f"PE达{pe:.1f}，需警惕估值风险")

        verdict = self._verdict(s)
        return ExpertScore(
            expert_name=self.NAME,
            philosophy=self.PHILOSOPHY,
            score=min(s, 100),
            verdict=verdict,
            reasoning=reasons,
        )

    @staticmethod
    def _verdict(s: float) -> ExpertVerdict:
        if s >= 70:
            return ExpertVerdict.STRONG_BUY
        if s >= 50:
            return ExpertVerdict.BUY
        if s >= 30:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID


class DuanYongpingStrategy:
    """段永平 —— 商业模式优先、护城河、本分投资。

    核心思想：
    1. 商业模式 > 管理层 > 价格（买股票就是买公司）
    2. 关注企业是否"本分"：做对的事情，把事情做对
    3. 护城河体现在用户粘性、品牌忠诚度、生态壁垒
    4. 不懂不做，宁可错过也不做错
    """

    NAME = "段永平"
    PHILOSOPHY = "商业模式优先 · 护城河 · 本分投资"

    def score(self, data: Dict[str, Any]) -> ExpertScore:
        s = 0.0
        reasons: List[str] = []

        roe = data.get("roe") or 0
        pe = data.get("pe") or 0
        pb = data.get("pb") or 0
        gross_margin = data.get("gross_margin") or 0
        net_margin = data.get("net_margin") or 0
        debt = data.get("debt_ratio") or 50
        revenue_growth = data.get("revenue_growth") or 0

        # 商业模式质量（通过毛利率和净利率间接判断）
        if gross_margin >= 50 and net_margin >= 20:
            s += 25
            reasons.append(f"毛利率{gross_margin:.1f}%、净利率{net_margin:.1f}%，商业模式优秀")
        elif gross_margin >= 35 and net_margin >= 12:
            s += 15
            reasons.append(f"毛利率{gross_margin:.1f}%、净利率{net_margin:.1f}%，商业模式良好")
        elif gross_margin >= 20:
            s += 5

        # ROE（段永平也看重资本回报）
        if roe >= 20:
            s += 20
            reasons.append(f"ROE为{roe:.1f}%，资本回报卓越")
        elif roe >= 15:
            s += 15
            reasons.append(f"ROE为{roe:.1f}%，盈利能力优秀")
        elif roe >= 10:
            s += 8
        else:
            reasons.append(f"ROE仅{roe:.1f}%，商业模式回报不足")

        # 财务健康（本分经营，不高杠杆）
        if debt < 30:
            s += 15
            reasons.append(f"负债率{debt:.1f}%，财务极为稳健")
        elif debt < 50:
            s += 8
        elif debt >= 60:
            reasons.append(f"负债率{debt:.1f}%，财务杠杆偏高")

        # 估值（段永平不追高，但愿意为好公司付合理价格）
        if 0 < pe <= 20:
            s += 15
            reasons.append(f"PE为{pe:.1f}，估值合理")
        elif 20 < pe <= 35:
            s += 8
        elif pe > 50:
            reasons.append(f"PE高达{pe:.1f}，即使是好公司也偏贵")

        # 增长稳健（不追求爆发式增长，但要稳）
        if 8 <= revenue_growth <= 30:
            s += 10
            reasons.append(f"营收增长{revenue_growth:.1f}%，增长稳健可持续")
        elif revenue_growth > 30:
            s += 5
            reasons.append(f"营收增长{revenue_growth:.1f}%，高增长可持续性待观察")

        # PB
        if 0 < pb <= 3:
            s += 5

        verdict = self._verdict(s)
        return ExpertScore(
            expert_name=self.NAME,
            philosophy=self.PHILOSOPHY,
            score=min(s, 100),
            verdict=verdict,
            reasoning=reasons,
        )

    @staticmethod
    def _verdict(s: float) -> ExpertVerdict:
        if s >= 65:
            return ExpertVerdict.STRONG_BUY
        if s >= 45:
            return ExpertVerdict.BUY
        if s >= 25:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID


class ZhangLeiStrategy:
    """张磊（高瓴资本） —— 长期主义、创新驱动、价值创造。

    核心思想：
    1. 长期主义：做时间的朋友，寻找具有长期结构性变化的行业
    2. 重仓中国：看好中国消费升级和科技创新
    3. 投资变化中的不变：消费者对美好生活的追求
    4. 赋能式投资：帮助企业创造价值而非简单套利
    """

    NAME = "张磊（高瓴）"
    PHILOSOPHY = "长期主义 · 创新驱动 · 价值创造"

    GROWTH_SECTORS = ["新能源", "半导体", "科技", "医药", "消费", "互联网", "人工智能"]

    def score(self, data: Dict[str, Any]) -> ExpertScore:
        s = 0.0
        reasons: List[str] = []

        roe = data.get("roe") or 0
        pe = data.get("pe") or 0
        pb = data.get("pb") or 0
        revenue_growth = data.get("revenue_growth") or 0
        rd_ratio = data.get("rd_ratio") or 0  # 研发投入占比
        gross_margin = data.get("gross_margin") or 0
        sector = data.get("sector", "")

        # 行业结构性机会
        if any(k in sector for k in self.GROWTH_SECTORS):
            s += 15
            reasons.append(f"行业「{sector}」具有长期结构性增长机会")

        # 高增长（张磊看重成长空间）
        if revenue_growth >= 30:
            s += 25
            reasons.append(f"营收增长{revenue_growth:.1f}%，高速成长")
        elif revenue_growth >= 15:
            s += 18
            reasons.append(f"营收增长{revenue_growth:.1f}%，快速增长")
        elif revenue_growth >= 8:
            s += 10
        elif revenue_growth <= 0:
            reasons.append(f"营收增长{revenue_growth:.1f}%，缺乏成长动力")

        # 研发投入（创新驱动）
        if rd_ratio >= 10:
            s += 15
            reasons.append(f"研发投入占比{rd_ratio:.1f}%，创新驱动明显")
        elif rd_ratio >= 5:
            s += 8
            reasons.append(f"研发投入占比{rd_ratio:.1f}%，有一定创新投入")
        elif rd_ratio > 0:
            s += 3

        # ROE（效率指标）
        if roe >= 18:
            s += 15
            reasons.append(f"ROE为{roe:.1f}%，资本效率高")
        elif roe >= 12:
            s += 10
        elif roe >= 8:
            s += 5

        # 毛利率（护城河宽度）
        if gross_margin >= 40:
            s += 10
            reasons.append(f"毛利率{gross_margin:.1f}%，具备竞争优势")
        elif gross_margin >= 25:
            s += 5

        # 估值容忍度（张磊愿意为高增长付溢价）
        if 0 < pe <= 40:
            s += 10
        elif 40 < pe <= 60:
            s += 5
            reasons.append(f"PE为{pe:.1f}，高增长对应一定溢价")
        elif pe > 80:
            reasons.append(f"PE高达{pe:.1f}，增长可能已被充分定价")

        # PB
        if 0 < pb <= 5:
            s += 5

        verdict = self._verdict(s)
        return ExpertScore(
            expert_name=self.NAME,
            philosophy=self.PHILOSOPHY,
            score=min(s, 100),
            verdict=verdict,
            reasoning=reasons,
        )

    @staticmethod
    def _verdict(s: float) -> ExpertVerdict:
        if s >= 70:
            return ExpertVerdict.STRONG_BUY
        if s >= 50:
            return ExpertVerdict.BUY
        if s >= 30:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID


class QiuGuoluStrategy:
    """邱国鹭 —— 价值投资实践、行业格局分析。

    核心思想：
    1. 行业格局比行业空间更重要：宁选月亮不选星星
    2. 价值投资的三个基本要素：好行业、好公司、好价格
    3. 看重行业集中度和龙头溢价
    4. 逆向投资：在行业低谷期布局龙头
    """

    NAME = "邱国鹭"
    PHILOSOPHY = "行业格局分析 · 龙头溢价 · 逆向投资"

    def score(self, data: Dict[str, Any]) -> ExpertScore:
        s = 0.0
        reasons: List[str] = []

        roe = data.get("roe") or 0
        pe = data.get("pe") or 0
        pb = data.get("pb") or 0
        debt = data.get("debt_ratio") or 50
        revenue_growth = data.get("revenue_growth") or 0
        market_cap = data.get("market_cap") or 0
        sector = data.get("sector", "")
        is_leader = data.get("is_industry_leader", False)

        # 行业龙头地位（邱国鹭最看重）
        if is_leader:
            s += 25
            reasons.append("行业龙头，享受格局溢价")
        elif market_cap and market_cap > 500_0000_0000:  # > 500亿
            s += 15
            reasons.append("大市值公司，可能是行业领先者")
        elif market_cap and market_cap > 100_0000_0000:  # > 100亿
            s += 8

        # PE 低估（好价格）
        if 0 < pe <= 12:
            s += 20
            reasons.append(f"PE仅{pe:.1f}，价格极具吸引力")
        elif 12 < pe <= 20:
            s += 12
            reasons.append(f"PE为{pe:.1f}，估值合理偏低")
        elif 20 < pe <= 30:
            s += 5
        elif pe > 40:
            reasons.append(f"PE达{pe:.1f}，价格偏贵")

        # PB 低估
        if 0 < pb <= 1.5:
            s += 12
            reasons.append(f"PB为{pb:.2f}，接近账面价值")
        elif 1.5 < pb <= 3:
            s += 6
        elif pb > 5:
            reasons.append(f"PB为{pb:.2f}，溢价过高")

        # ROE（好公司的核心指标）
        if roe >= 18:
            s += 15
            reasons.append(f"ROE为{roe:.1f}%，盈利质量高")
        elif roe >= 12:
            s += 10
        elif roe >= 8:
            s += 5

        # 财务稳健
        if debt < 40:
            s += 8
            reasons.append(f"负债率{debt:.1f}%，财务稳健")
        elif debt >= 65:
            reasons.append(f"负债率{debt:.1f}%，需注意财务风险")

        # 增长适度（邱国鹭不喜欢过度高增长，更看重确定性）
        if 5 <= revenue_growth <= 20:
            s += 10
            reasons.append(f"营收增长{revenue_growth:.1f}%，增长确定性高")
        elif revenue_growth > 30:
            s += 3
            reasons.append(f"营收增长{revenue_growth:.1f}%，高增长可持续性存疑")

        verdict = self._verdict(s)
        return ExpertScore(
            expert_name=self.NAME,
            philosophy=self.PHILOSOPHY,
            score=min(s, 100),
            verdict=verdict,
            reasoning=reasons,
        )

    @staticmethod
    def _verdict(s: float) -> ExpertVerdict:
        if s >= 65:
            return ExpertVerdict.STRONG_BUY
        if s >= 45:
            return ExpertVerdict.BUY
        if s >= 25:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID


# ---------------------------------------------------------------------------
# 综合分析器
# ---------------------------------------------------------------------------

# 专家权重（可按需调整）
EXPERT_WEIGHTS: Dict[str, float] = {
    "沃伦·巴菲特": 1.2,
    "查理·芒格": 1.1,
    "彼得·林奇": 1.0,
    "本杰明·格雷厄姆": 1.0,
    "霍华德·马克斯": 0.9,
    "但斌": 1.0,
    "林园": 1.0,
    "段永平": 1.1,
    "张磊（高瓴）": 1.0,
    "邱国鹭": 0.9,
}


class ExpertStrategyAnalyzer:
    """综合专家策略分析器。

    将十位投资大师的独立评分汇总为综合推荐，支持批量分析。
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self._strategies = [
            BuffettStrategy(),
            MungerStrategy(),
            LynchStrategy(),
            GrahamStrategy(),
            HowardMarksStrategy(),
            DanBinStrategy(),
            LinYuanStrategy(),
            DuanYongpingStrategy(),
            ZhangLeiStrategy(),
            QiuGuoluStrategy(),
        ]
        self._weights = weights or EXPERT_WEIGHTS

    def analyze_stock(self, stock_data: Dict[str, Any]) -> Optional[ExpertAnalysisResult]:
        """使用全部专家策略分析单只股票。

        Args:
            stock_data: 股票数据字典，需包含 pe, pb, roe 等字段。

        Returns:
            ExpertAnalysisResult 或 None（数据不足时）。
        """
        code = stock_data.get("code", "")
        name = stock_data.get("name", "")

        if not stock_data.get("pe") and not stock_data.get("roe"):
            logger.warning(f"股票 {code} {name} 缺少关键财务数据，跳过专家分析")
            return None

        expert_scores: List[ExpertScore] = []
        for strategy in self._strategies:
            try:
                score = strategy.score(stock_data)
                expert_scores.append(score)
            except Exception as e:
                logger.error(f"{strategy.NAME} 评分异常({code}): {e}")

        if not expert_scores:
            return None

        # 加权综合分
        total_weight = 0.0
        weighted_sum = 0.0
        for es in expert_scores:
            w = self._weights.get(es.expert_name, 1.0)
            weighted_sum += es.score * w
            total_weight += w

        composite_score = weighted_sum / total_weight if total_weight > 0 else 0
        composite_verdict = self._composite_verdict(composite_score)

        # 汇总核心理由（取各专家最高分的理由）
        top_reasons = self._extract_top_reasons(expert_scores)
        consensus_summary = self._build_consensus(expert_scores, composite_score, composite_verdict)

        return ExpertAnalysisResult(
            code=code,
            name=name,
            expert_scores=expert_scores,
            composite_score=round(composite_score, 1),
            composite_verdict=composite_verdict,
            top_reasons=top_reasons,
            consensus_summary=consensus_summary,
        )

    def analyze_multiple(
        self, stocks: List[Dict[str, Any]], top_n: int = 20
    ) -> List[ExpertAnalysisResult]:
        """批量分析并返回综合得分最高的 top_n 只股票。"""
        results: List[ExpertAnalysisResult] = []
        for stock in stocks:
            result = self.analyze_stock(stock)
            if result:
                results.append(result)

        results.sort(key=lambda r: r.composite_score, reverse=True)
        return results[:top_n]

    def get_expert_details(self, result: ExpertAnalysisResult) -> Dict[str, Any]:
        """获取单只股票各专家的详细评分。"""
        return {
            "code": result.code,
            "name": result.name,
            "composite_score": result.composite_score,
            "composite_verdict": result.composite_verdict.value,
            "expert_details": [
                {
                    "expert": es.expert_name,
                    "philosophy": es.philosophy,
                    "score": es.score,
                    "verdict": es.verdict.value,
                    "reasoning": es.reasoning,
                    "key_metrics": es.key_metrics,
                }
                for es in result.expert_scores
            ],
        }

    @staticmethod
    def _composite_verdict(score: float) -> ExpertVerdict:
        if score >= 65:
            return ExpertVerdict.STRONG_BUY
        if score >= 45:
            return ExpertVerdict.BUY
        if score >= 28:
            return ExpertVerdict.HOLD
        return ExpertVerdict.AVOID

    @staticmethod
    def _extract_top_reasons(scores: List[ExpertScore], max_reasons: int = 8) -> List[str]:
        """从各专家理由中提取最重要的几条。"""
        all_reasons: List[str] = []
        for es in scores:
            if es.score >= 40:
                all_reasons.extend(es.reasoning[:2])
        # 去重保序
        seen = set()
        unique: List[str] = []
        for r in all_reasons:
            if r not in seen:
                seen.add(r)
                unique.append(r)
        return unique[:max_reasons]

    @staticmethod
    def _build_consensus(
        scores: List[ExpertScore], composite_score: float, verdict: ExpertVerdict
    ) -> str:
        """构建专家共识摘要。"""
        bullish = sum(1 for es in scores if es.verdict in (ExpertVerdict.STRONG_BUY, ExpertVerdict.BUY))
        hold = sum(1 for es in scores if es.verdict == ExpertVerdict.HOLD)
        bearish = sum(1 for es in scores if es.verdict == ExpertVerdict.AVOID)
        total = len(scores)

        parts = [f"综合评分{composite_score:.1f}分，{verdict.value}"]
        parts.append(f"十位大师中{bullish}位看好、{hold}位观望、{bearish}位不看好")

        if bullish >= 7:
            parts.append("高度共识，多数专家认可投资价值")
        elif bullish >= 4:
            parts.append("共识度中等，建议结合自身判断")
        else:
            parts.append("分歧较大，需谨慎对待")

        return "。".join(parts)


# ---------------------------------------------------------------------------
# 格式化输出
# ---------------------------------------------------------------------------

def format_expert_analysis(result: ExpertAnalysisResult) -> str:
    """将专家分析结果格式化为可读文本。"""
    lines = [
        f"{'='*60}",
        f"🎓 专家策略分析报告 —— {result.name} ({result.code})",
        f"{'='*60}",
        "",
        f"🏆 综合评级: {result.composite_verdict.value}",
        f"📊 综合评分: {result.composite_score}/100",
        "",
        f"📝 共识摘要: {result.consensus_summary}",
        "",
        f"{'─'*60}",
        "📋 各专家评分明细:",
        f"{'─'*60}",
    ]

    for es in result.expert_scores:
        bar = "█" * int(es.score / 10) + "░" * (10 - int(es.score / 10))
        lines.append(f"  {es.expert_name:<16} [{bar}] {es.score:>5.1f}分  {es.verdict.value}")
        for r in es.reasoning[:2]:
            lines.append(f"    └─ {r}")
        lines.append("")

    lines.append(f"{'─'*60}")
    lines.append("✅ 核心看点:")
    for r in result.top_reasons:
        lines.append(f"  • {r}")

    lines.append("")
    lines.append(f"{'='*60}")
    return "\n".join(lines)


def format_expert_batch_report(results: List[ExpertAnalysisResult]) -> str:
    """格式化批量分析汇总报告。"""
    lines = [
        f"{'='*60}",
        f"🎓 专家策略批量分析报告（共{len(results)}只）",
        f"{'='*60}",
        "",
        f"{'排名':<4} {'代码':<8} {'名称':<10} {'综合分':>6} {'评级':<8} {'看好人数':>6}",
        f"{'─'*60}",
    ]

    for i, r in enumerate(results, 1):
        bullish_count = sum(
            1 for es in r.expert_scores
            if es.verdict in (ExpertVerdict.STRONG_BUY, ExpertVerdict.BUY)
        )
        lines.append(
            f" {i:<3} {r.code:<8} {r.name:<10} {r.composite_score:>5.1f} "
            f"{r.composite_verdict.value:<8} {bullish_count:>4}/10"
        )

    lines.append(f"{'─'*60}")
    lines.append("")
    lines.append("注：看好人数为十位专家中给出「强烈推荐」或「推荐买入」的数量")
    lines.append(f"{'='*60}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 入口（可独立运行测试）
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    demo_data = [
        {
            "code": "600519",
            "name": "贵州茅台",
            "price": 1800,
            "pe": 30,
            "pb": 10,
            "roe": 30,
            "debt_ratio": 20,
            "revenue_growth": 15,
            "net_margin": 50,
            "gross_margin": 90,
            "dividend_yield": 1.5,
            "sector": "白酒",
            "current_ratio": 3.5,
            "earnings_growth": 15,
            "is_industry_leader": True,
        },
        {
            "code": "300750",
            "name": "宁德时代",
            "price": 220,
            "pe": 25,
            "pb": 6,
            "roe": 22,
            "debt_ratio": 55,
            "revenue_growth": 30,
            "net_margin": 12,
            "gross_margin": 22,
            "dividend_yield": 0.3,
            "sector": "新能源",
            "current_ratio": 1.8,
            "rd_ratio": 7,
            "earnings_growth": 30,
            "is_industry_leader": True,
        },
        {
            "code": "000858",
            "name": "五粮液",
            "price": 150,
            "pe": 20,
            "pb": 5,
            "roe": 25,
            "debt_ratio": 25,
            "revenue_growth": 12,
            "net_margin": 38,
            "gross_margin": 75,
            "dividend_yield": 2.5,
            "sector": "白酒",
            "current_ratio": 3.0,
            "earnings_growth": 12,
            "is_industry_leader": True,
        },
    ]

    analyzer = ExpertStrategyAnalyzer()
    results = analyzer.analyze_multiple(demo_data, top_n=10)

    print(format_expert_batch_report(results))
    print()

    for r in results:
        print(format_expert_analysis(r))
        print()
