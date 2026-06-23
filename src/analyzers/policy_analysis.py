"""政策分析模块 — 中国政策对A股板块的影响分析。

涵盖：
- 十四五规划重点领域
- 当前政策热点（新质生产力、人工智能+、低空经济等）
- 政策→板块→个股映射
- 政策动量追踪
- 政策面投资建议生成
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger


# ===========================================================================
# 枚举与数据类
# ===========================================================================

class PolicyLevel(Enum):
    """政策级别。"""
    NATIONAL = "国家战略"      # 五年规划、中央经济工作会议
    MINISTERIAL = "部委政策"    # 部委发文、行动计划
    LOCAL = "地方政策"          # 省市级政策
    GUIDANCE = "指导意见"       # 方向性指引


class Momentum(Enum):
    """政策动量等级。"""
    BLAZING = "极强"       # 持续密集出台、高层反复强调
    STRONG = "强"          # 多部委联合推动
    MODERATE = "中等"      # 有相关政策出台
    WEAK = "弱"            # 提及但未重点推进
    DORMANT = "休眠"       # 暂无新政策


@dataclass
class PolicyArea:
    """政策领域定义。"""
    name: str
    description: str
    level: PolicyLevel
    keywords: List[str]
    related_sectors: List[str]
    momentum: Momentum
    recent_actions: List[str] = field(default_factory=list)
    stock_targets: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class PolicyScore:
    """个股政策面评分。"""
    code: str
    name: str
    total_score: float
    matched_areas: List[str]
    matched_sectors: List[str]
    momentum_bonus: float
    level_bonus: float
    details: List[str] = field(default_factory=list)


# ===========================================================================
# 十四五规划重点领域映射
# ===========================================================================

FIVE_YEAR_PLAN: Dict[str, Dict[str, Any]] = {
    "科技创新": {
        "description": "新一代人工智能、量子信息、集成电路、脑科学、基因与生物技术、临床医学与健康",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.BLAZING,
        "keywords": [
            "科技创新", "人工智能", "量子信息", "集成电路", "芯片",
            "脑科学", "基因", "生物技术", "临床医学", "科技自立",
            "基础研究", "关键核心技术", "卡脖子",
        ],
        "related_sectors": [
            "半导体", "芯片", "人工智能", "量子计算", "生物科技",
            "医药研发", "医疗器械",
        ],
        "stock_targets": [
            {"code": "688256", "name": "寒武纪", "reason": "AI推理芯片龙头"},
            {"code": "688041", "name": "海光信息", "reason": "国产CPU/DCU"},
            {"code": "300474", "name": "景嘉微", "reason": "国产GPU"},
            {"code": "688012", "name": "中微公司", "reason": "刻蚀设备龙头"},
            {"code": "688019", "name": "安集科技", "reason": "CMP抛光液龙头"},
            {"code": "002049", "name": "紫光国微", "reason": "特种芯片"},
            {"code": "300308", "name": "中际旭创", "reason": "光模块龙头"},
        ],
    },
    "新型基础设施": {
        "description": "5G、工业互联网、数据中心、人工智能",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.STRONG,
        "keywords": [
            "新基建", "5G", "工业互联网", "数据中心", "算力",
            "东数西算", "云计算", "边缘计算", "物联网",
        ],
        "related_sectors": [
            "通信设备", "5G", "数据中心", "云计算", "物联网",
            "光通信", "服务器",
        ],
        "stock_targets": [
            {"code": "000977", "name": "浪潮信息", "reason": "AI服务器龙头"},
            {"code": "603019", "name": "中科曙光", "reason": "高性能计算"},
            {"code": "300308", "name": "中际旭创", "reason": "800G光模块"},
            {"code": "300502", "name": "新易盛", "reason": "高速光模块"},
            {"code": "002281", "name": "兴迅科技", "reason": "光通信器件"},
        ],
    },
    "数字经济": {
        "description": "数字中国、数据要素市场",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.BLAZING,
        "keywords": [
            "数字经济", "数字中国", "数据要素", "数据资产",
            "数据交易", "数字化转型", "数字政府", "智慧城市",
        ],
        "related_sectors": [
            "软件", "IT服务", "大数据", "信息安全", "智慧城市",
            "数据要素", "金融科技",
        ],
        "stock_targets": [
            {"code": "688111", "name": "金山办公", "reason": "国产办公软件"},
            {"code": "600588", "name": "用友网络", "reason": "企业数字化"},
            {"code": "002405", "name": "四维图新", "reason": "数据资产"},
            {"code": "300033", "name": "同花顺", "reason": "金融数据"},
        ],
    },
    "绿色发展": {
        "description": "碳达峰碳中和、新能源、节能环保",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.STRONG,
        "keywords": [
            "碳达峰", "碳中和", "新能源", "光伏", "风电",
            "储能", "氢能", "节能环保", "绿色低碳", "碳交易",
        ],
        "related_sectors": [
            "光伏", "风电", "储能", "新能源汽车", "环保",
            "锂电池", "氢能",
        ],
        "stock_targets": [
            {"code": "300750", "name": "宁德时代", "reason": "锂电池龙头"},
            {"code": "601012", "name": "隆基绿能", "reason": "光伏龙头"},
            {"code": "002459", "name": "晶澳科技", "reason": "光伏组件"},
            {"code": "300274", "name": "阳光电源", "reason": "逆变器+储能"},
            {"code": "600438", "name": "通威股份", "reason": "硅料+电池"},
        ],
    },
    "制造强国": {
        "description": "高端制造、智能制造、专精特新",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.STRONG,
        "keywords": [
            "制造强国", "高端制造", "智能制造", "专精特新",
            "工业母机", "机器人", "数控机床", "工业软件",
        ],
        "related_sectors": [
            "机器人", "工业母机", "智能制造", "工业软件",
            "航空航天", "高端装备",
        ],
        "stock_targets": [
            {"code": "300124", "name": "汇川技术", "reason": "工控龙头"},
            {"code": "688169", "name": "石头科技", "reason": "智能硬件"},
            {"code": "002747", "name": "埃斯顿", "reason": "工业机器人"},
            {"code": "688009", "name": "中国通号", "reason": "轨交控制系统"},
        ],
    },
    "扩大内需": {
        "description": "消费升级、乡村振兴",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.MODERATE,
        "keywords": [
            "扩大内需", "消费升级", "乡村振兴", "共同富裕",
            "新型消费", "服务消费", "县域经济",
        ],
        "related_sectors": [
            "白酒", "食品饮料", "家电", "零售",
            "农业", "旅游", "教育",
        ],
        "stock_targets": [
            {"code": "600519", "name": "贵州茅台", "reason": "白酒龙头"},
            {"code": "000858", "name": "五粮液", "reason": "高端白酒"},
            {"code": "000333", "name": "美的集团", "reason": "家电龙头"},
            {"code": "002714", "name": "牧原股份", "reason": "养猪龙头"},
        ],
    },
    "区域发展": {
        "description": "京津冀、长三角、粤港澳、成渝",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.MODERATE,
        "keywords": [
            "京津冀", "长三角", "粤港澳", "成渝",
            "雄安新区", "大湾区", "区域一体化",
        ],
        "related_sectors": [
            "基建", "房地产", "交通运输", "物流",
        ],
        "stock_targets": [
            {"code": "601668", "name": "中国建筑", "reason": "基建龙头"},
            {"code": "600048", "name": "保利发展", "reason": "央企地产"},
        ],
    },
    "一带一路": {
        "description": "国际合作",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.MODERATE,
        "keywords": [
            "一带一路", "国际合作", "出海", "中欧班列",
            "海外基建", "人民币国际化",
        ],
        "related_sectors": [
            "工程建设", "工程机械", "国际物流", "跨境电商",
        ],
        "stock_targets": [
            {"code": "601390", "name": "中国中铁", "reason": "海外基建"},
            {"code": "600031", "name": "三一重工", "reason": "工程机械出海"},
        ],
    },
}


# ===========================================================================
# 当前政策热点
# ===========================================================================

CURRENT_HOTSPOTS: Dict[str, Dict[str, Any]] = {
    "新质生产力": {
        "description": "以科技创新为核心的先进生产力形态",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.BLAZING,
        "keywords": [
            "新质生产力", "新型生产力", "创新驱动", "科技成果转化",
            "原创性", "颠覆性技术",
        ],
        "related_sectors": [
            "人工智能", "量子计算", "生物技术", "新能源",
            "新材料", "高端装备", "半导体",
        ],
        "recent_actions": [
            "2024年政府工作报告首次提出",
            "中央经济工作会议重点强调",
            "各部委密集出台配套政策",
            "地方两会普遍列入重点工作",
        ],
        "stock_targets": [
            {"code": "688256", "name": "寒武纪", "reason": "AI芯片代表"},
            {"code": "688041", "name": "海光信息", "reason": "国产算力"},
            {"code": "300124", "name": "汇川技术", "reason": "智能制造代表"},
            {"code": "300750", "name": "宁德时代", "reason": "新能源龙头"},
        ],
    },
    "人工智能+": {
        "description": "AI与各行业深度融合",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.BLAZING,
        "keywords": [
            "人工智能+", "AI+", "大模型", "生成式AI",
            "智能体", "具身智能", "AI应用",
        ],
        "related_sectors": [
            "人工智能", "软件", "云计算", "大数据",
            "机器人", "自动驾驶", "智能硬件",
        ],
        "recent_actions": [
            "2024年政府工作报告提出'人工智能+'行动",
            "各地出台AI产业发展规划",
            "大模型备案制度落地",
            "AI+制造/医疗/教育专项政策",
        ],
        "stock_targets": [
            {"code": "688256", "name": "寒武纪", "reason": "AI芯片"},
            {"code": "688111", "name": "金山办公", "reason": "AI+办公"},
            {"code": "002230", "name": "科大讯飞", "reason": "AI+语音"},
            {"code": "688041", "name": "海光信息", "reason": "AI算力"},
            {"code": "300308", "name": "中际旭创", "reason": "AI光互联"},
        ],
    },
    "低空经济": {
        "description": "无人机、eVTOL、低空空域管理",
        "level": PolicyLevel.MINISTERIAL,
        "momentum": Momentum.STRONG,
        "keywords": [
            "低空经济", "eVTOL", "飞行汽车", "无人机",
            "低空空域", "通用航空", "城市空中交通",
        ],
        "related_sectors": [
            "航空航天", "无人机", "通用航空", "新材料",
            "电池", "电机", "飞控系统",
        ],
        "recent_actions": [
            "2024年首次写入政府工作报告",
            "多地出台低空经济发展规划",
            "空域管理改革试点推进",
            "适航认证加速",
        ],
        "stock_targets": [
            {"code": "002097", "name": "山河智能", "reason": "通航设备"},
            {"code": "002013", "name": "中航机电", "reason": "航空机电"},
            {"code": "300450", "name": "先导智能", "reason": "电池设备"},
            {"code": "002389", "name": "航天彩虹", "reason": "军用无人机"},
            {"code": "688122", "name": "西部超导", "reason": "航空材料"},
        ],
    },
    "数据要素": {
        "description": "数据确权、数据交易、数据资产入表",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.STRONG,
        "keywords": [
            "数据要素", "数据资产", "数据确权", "数据交易",
            "数据资产入表", "数据二十条", "数据局",
        ],
        "related_sectors": [
            "大数据", "信息安全", "数据服务", "金融科技",
            "智慧城市", "IT服务",
        ],
        "recent_actions": [
            "国家数据局成立",
            "数据资产入表政策落地",
            "各地数据交易所设立",
            "数据二十条发布",
        ],
        "stock_targets": [
            {"code": "002405", "name": "四维图新", "reason": "数据资产"},
            {"code": "300033", "name": "同花顺", "reason": "金融数据"},
            {"code": "600588", "name": "用友网络", "reason": "企业数据"},
            {"code": "300188", "name": "美亚柏科", "reason": "数据安全"},
        ],
    },
    "国产替代": {
        "description": "关键技术和核心零部件自主可控",
        "level": PolicyLevel.NATIONAL,
        "momentum": Momentum.BLAZING,
        "keywords": [
            "国产替代", "自主可控", "信创", "国产化",
            "安全可控", "供应链安全", "去美化",
        ],
        "related_sectors": [
            "半导体", "操作系统", "数据库", "中间件",
            "办公软件", "ERP", "工业软件", "服务器",
        ],
        "recent_actions": [
            "信创产业持续深化",
            "政府采购优先国产",
            "半导体设备国产化率提升",
            "EDA/IP国产化推进",
        ],
        "stock_targets": [
            {"code": "688041", "name": "海光信息", "reason": "国产CPU"},
            {"code": "300474", "name": "景嘉微", "reason": "国产GPU"},
            {"code": "688111", "name": "金山办公", "reason": "国产办公"},
            {"code": "688012", "name": "中微公司", "reason": "国产设备"},
            {"code": "688019", "name": "安集科技", "reason": "国产材料"},
            {"code": "002049", "name": "紫光国微", "reason": "国产芯片"},
            {"code": "600588", "name": "用友网络", "reason": "国产ERP"},
            {"code": "000977", "name": "浪潮信息", "reason": "国产服务器"},
        ],
    },
}


# ===========================================================================
# 权重配置
# ===========================================================================

MOMENTUM_WEIGHTS = {
    Momentum.BLAZING: 3.0,
    Momentum.STRONG: 2.0,
    Momentum.MODERATE: 1.0,
    Momentum.WEAK: 0.5,
    Momentum.DORMANT: 0.0,
}

LEVEL_WEIGHTS = {
    PolicyLevel.NATIONAL: 3.0,
    PolicyLevel.MINISTERIAL: 2.0,
    PolicyLevel.LOCAL: 1.0,
    PolicyLevel.GUIDANCE: 0.5,
}


# ===========================================================================
# 政策分析器
# ===========================================================================

class PolicyAnalyzer:
    """政策对A股板块影响分析器。

    功能：
    1. 政策领域 → 板块 → 个股 映射
    2. 个股政策面评分
    3. 政策动量追踪
    4. 政策面投资建议
    """

    def __init__(self):
        self._all_areas: Dict[str, Dict[str, Any]] = {}
        self._all_areas.update(FIVE_YEAR_PLAN)
        self._all_areas.update(CURRENT_HOTSPOTS)
        self._stock_index: Dict[str, List[str]] = {}  # code -> [area_name, ...]
        self._sector_index: Dict[str, List[str]] = {}  # sector -> [area_name, ...]
        self._build_indices()

    def _build_indices(self):
        """构建反向索引：个股→政策、板块→政策。"""
        self._stock_index.clear()
        self._sector_index.clear()

        for area_name, area_data in self._all_areas.items():
            # 个股索引
            for target in area_data.get("stock_targets", []):
                code = target["code"]
                if code not in self._stock_index:
                    self._stock_index[code] = []
                if area_name not in self._stock_index[code]:
                    self._stock_index[code].append(area_name)

            # 板块索引
            for sector in area_data.get("related_sectors", []):
                if sector not in self._sector_index:
                    self._sector_index[sector] = []
                if area_name not in self._sector_index[sector]:
                    self._sector_index[sector].append(area_name)

    # -----------------------------------------------------------------------
    # 查询接口
    # -----------------------------------------------------------------------

    def get_all_policy_areas(self) -> List[Dict[str, Any]]:
        """获取所有政策领域概览。"""
        result = []
        for name, data in self._all_areas.items():
            result.append({
                "name": name,
                "description": data["description"],
                "level": data["level"].value,
                "momentum": data["momentum"].value,
                "related_sectors": data["related_sectors"],
                "stock_count": len(data.get("stock_targets", [])),
            })
        return result

    def get_five_year_plan_areas(self) -> List[Dict[str, Any]]:
        """获取十四五规划重点领域。"""
        result = []
        for name, data in FIVE_YEAR_PLAN.items():
            result.append({
                "name": name,
                "description": data["description"],
                "level": data["level"].value,
                "momentum": data["momentum"].value,
                "related_sectors": data["related_sectors"],
                "stock_count": len(data.get("stock_targets", [])),
            })
        return result

    def get_current_hotspots(self) -> List[Dict[str, Any]]:
        """获取当前政策热点。"""
        result = []
        for name, data in CURRENT_HOTSPOTS.items():
            result.append({
                "name": name,
                "description": data["description"],
                "level": data["level"].value,
                "momentum": data["momentum"].value,
                "recent_actions": data.get("recent_actions", []),
                "related_sectors": data["related_sectors"],
                "stock_count": len(data.get("stock_targets", [])),
            })
        return result

    def get_policy_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """按名称获取政策领域详情。"""
        data = self._all_areas.get(name)
        if not data:
            return None
        return {
            "name": name,
            "description": data["description"],
            "level": data["level"].value,
            "momentum": data["momentum"].value,
            "keywords": data["keywords"],
            "related_sectors": data["related_sectors"],
            "recent_actions": data.get("recent_actions", []),
            "stock_targets": data.get("stock_targets", []),
        }

    def get_sectors_for_policy(self, policy_name: str) -> List[str]:
        """获取政策相关板块列表。"""
        data = self._all_areas.get(policy_name)
        if not data:
            return []
        return data.get("related_sectors", [])

    def get_stocks_for_policy(self, policy_name: str) -> List[Dict[str, str]]:
        """获取政策相关个股列表。"""
        data = self._all_areas.get(policy_name)
        if not data:
            return []
        return data.get("stock_targets", [])

    def get_policies_for_stock(self, code: str) -> List[Dict[str, Any]]:
        """获取个股关联的所有政策领域。"""
        area_names = self._stock_index.get(code, [])
        result = []
        for name in area_names:
            area = self.get_policy_by_name(name)
            if area:
                result.append(area)
        return result

    def get_policies_for_sector(self, sector: str) -> List[Dict[str, Any]]:
        """获取板块关联的所有政策领域。"""
        area_names = self._sector_index.get(sector, [])
        result = []
        for name in area_names:
            area = self.get_policy_by_name(name)
            if area:
                result.append(area)
        return result

    # -----------------------------------------------------------------------
    # 评分接口
    # -----------------------------------------------------------------------

    def score_stock(self, code: str, name: str = "") -> Optional[PolicyScore]:
        """对单只股票进行政策面评分。

        评分逻辑：
        - 基础分 = 匹配到的政策领域数量 × 2
        - 动量加分 = Σ(动量权重)
        - 级别加分 = Σ(级别权重)
        - 总分上限 30 分
        """
        area_names = self._stock_index.get(code, [])
        if not area_names:
            return PolicyScore(
                code=code,
                name=name,
                total_score=0.0,
                matched_areas=[],
                matched_sectors=[],
                momentum_bonus=0.0,
                level_bonus=0.0,
                details=["未匹配到任何政策领域"],
            )

        matched_areas = []
        matched_sectors_set: Set[str] = set()
        momentum_bonus = 0.0
        level_bonus = 0.0
        details = []

        for area_name in area_names:
            data = self._all_areas.get(area_name)
            if not data:
                continue

            matched_areas.append(area_name)

            # 找到该股票在此政策中的具体原因
            for target in data.get("stock_targets", []):
                if target["code"] == code:
                    details.append(
                        f"【{area_name}】{target['reason']}"
                    )
                    break

            # 板块收集
            for sector in data.get("related_sectors", []):
                matched_sectors_set.add(sector)

            # 动量加分
            mom = data.get("momentum", Momentum.DORMANT)
            momentum_bonus += MOMENTUM_WEIGHTS.get(mom, 0.0)

            # 级别加分
            lvl = data.get("level", PolicyLevel.GUIDANCE)
            level_bonus += LEVEL_WEIGHTS.get(lvl, 0.0)

        base_score = len(matched_areas) * 2.0
        total = min(base_score + momentum_bonus + level_bonus, 30.0)

        return PolicyScore(
            code=code,
            name=name,
            total_score=round(total, 2),
            matched_areas=matched_areas,
            matched_sectors=sorted(matched_sectors_set),
            momentum_bonus=round(momentum_bonus, 2),
            level_bonus=round(level_bonus, 2),
            details=details,
        )

    def score_stocks(self, stocks: List[Dict[str, Any]]) -> List[PolicyScore]:
        """批量对股票进行政策面评分。

        Args:
            stocks: [{"code": "688256", "name": "寒武纪", ...}, ...]

        Returns:
            按政策分降序排列的评分列表。
        """
        results = []
        for stock in stocks:
            code = stock.get("code", "")
            name = stock.get("name", "")
            score = self.score_stock(code, name)
            if score and score.total_score > 0:
                results.append(score)

        results.sort(key=lambda x: x.total_score, reverse=True)
        return results

    def score_stock_by_sector(self, sector: str) -> List[PolicyScore]:
        """通过板块名称查找相关个股并评分。

        从所有政策领域的 stock_targets 中筛选属于该板块的个股，
        若无法精确匹配板块则返回空列表。
        """
        area_names = self._sector_index.get(sector, [])
        if not area_names:
            return []

        seen_codes: Set[str] = set()
        candidates: List[Dict[str, str]] = []

        for area_name in area_names:
            data = self._all_areas.get(area_name)
            if not data:
                continue
            for target in data.get("stock_targets", []):
                if target["code"] not in seen_codes:
                    seen_codes.add(target["code"])
                    candidates.append(target)

        return self.score_stocks(candidates)

    # -----------------------------------------------------------------------
    # 政策动量
    # -----------------------------------------------------------------------

    def get_momentum_ranking(self) -> List[Dict[str, Any]]:
        """获取政策动量排名（从强到弱）。"""
        ranking = []
        for name, data in self._all_areas.items():
            mom = data.get("momentum", Momentum.DORMANT)
            lvl = data.get("level", PolicyLevel.GUIDANCE)
            score = MOMENTUM_WEIGHTS.get(mom, 0) + LEVEL_WEIGHTS.get(lvl, 0)
            ranking.append({
                "name": name,
                "momentum": mom.value,
                "level": lvl.value,
                "score": score,
                "description": data["description"],
            })

        ranking.sort(key=lambda x: x["score"], reverse=True)
        return ranking

    def get_blazing_policies(self) -> List[Dict[str, Any]]:
        """获取当前动量极强的政策领域。"""
        return [
            item for item in self.get_momentum_ranking()
            if item["momentum"] == Momentum.BLAZING.value
        ]

    # -----------------------------------------------------------------------
    # 投资建议
    # -----------------------------------------------------------------------

    def generate_recommendations(
        self,
        top_n: int = 10,
        min_score: float = 5.0,
    ) -> List[Dict[str, Any]]:
        """生成政策面投资建议。

        逻辑：
        1. 遍历所有政策领域中的个股
        2. 政策面评分
        3. 按评分排序，取 top_n
        4. 生成推荐理由

        Args:
            top_n: 返回前N只股票
            min_score: 最低政策分阈值

        Returns:
            推荐列表。
        """
        # 收集所有候选个股
        all_targets: Dict[str, Dict[str, str]] = {}
        for data in self._all_areas.values():
            for target in data.get("stock_targets", []):
                code = target["code"]
                if code not in all_targets:
                    all_targets[code] = target

        # 评分
        scores = self.score_stocks(list(all_targets.values()))

        # 过滤
        filtered = [s for s in scores if s.total_score >= min_score]

        # 构建推荐
        recommendations = []
        for ps in filtered[:top_n]:
            # 判断是否属于当前热点
            hotspot_tags = []
            for area_name in ps.matched_areas:
                if area_name in CURRENT_HOTSPOTS:
                    hotspot_tags.append(area_name)

            # 确定推荐等级
            if ps.total_score >= 20:
                level = "强烈推荐"
                action = "重点关注"
            elif ps.total_score >= 12:
                level = "推荐"
                action = "适当配置"
            elif ps.total_score >= 6:
                level = "关注"
                action = "纳入观察"
            else:
                level = "一般"
                action = "暂不操作"

            recommendations.append({
                "code": ps.code,
                "name": ps.name,
                "policy_score": ps.total_score,
                "recommendation_level": level,
                "action": action,
                "matched_areas": ps.matched_areas,
                "hotspot_tags": hotspot_tags,
                "related_sectors": ps.matched_sectors,
                "momentum_bonus": ps.momentum_bonus,
                "level_bonus": ps.level_bonus,
                "reasons": ps.details,
            })

        return recommendations

    def generate_hotspot_recommendations(self) -> List[Dict[str, Any]]:
        """专门针对当前政策热点生成推荐。"""
        all_targets: Dict[str, Dict[str, str]] = {}
        for name, data in CURRENT_HOTSPOTS.items():
            for target in data.get("stock_targets", []):
                code = target["code"]
                if code not in all_targets:
                    all_targets[code] = target

        scores = self.score_stocks(list(all_targets.values()))

        results = []
        for ps in scores:
            if ps.total_score <= 0:
                continue

            # 标注所属热点
            hotspot_tags = [
                area for area in ps.matched_areas
                if area in CURRENT_HOTSPOTS
            ]

            results.append({
                "code": ps.code,
                "name": ps.name,
                "policy_score": ps.total_score,
                "hotspot_tags": hotspot_tags,
                "reasons": ps.details,
                "related_sectors": ps.matched_sectors,
            })

        results.sort(key=lambda x: x["policy_score"], reverse=True)
        return results

    # -----------------------------------------------------------------------
    # 综合分析
    # -----------------------------------------------------------------------

    def full_analysis(self, stock_code: str, stock_name: str = "") -> Dict[str, Any]:
        """对单只股票进行完整的政策面分析。"""
        ps = self.score_stock(stock_code, stock_name)
        if not ps:
            return {
                "code": stock_code,
                "name": stock_name,
                "error": "无法评分",
            }

        related_policies = self.get_policies_for_stock(stock_code)

        # 判断是否属于当前热点
        in_hotspots = [
            area_name for area_name in ps.matched_areas
            if area_name in CURRENT_HOTSPOTS
        ]

        # 判断是否属于十四五规划
        in_five_year = [
            area_name for area_name in ps.matched_areas
            if area_name in FIVE_YEAR_PLAN
        ]

        # 政策前景判断
        max_momentum = Momentum.DORMANT
        for area_name in ps.matched_areas:
            data = self._all_areas.get(area_name)
            if data:
                mom = data.get("momentum", Momentum.DORMANT)
                if MOMENTUM_WEIGHTS.get(mom, 0) > MOMENTUM_WEIGHTS.get(max_momentum, 0):
                    max_momentum = mom

        if max_momentum == Momentum.BLAZING:
            outlook = "政策风口，持续受益"
        elif max_momentum == Momentum.STRONG:
            outlook = "政策支撑，中期看好"
        elif max_momentum == Momentum.MODERATE:
            outlook = "政策平稳，中性偏多"
        elif max_momentum == Momentum.WEAK:
            outlook = "政策关注度一般"
        else:
            outlook = "暂无明确政策催化"

        return {
            "code": stock_code,
            "name": stock_name,
            "policy_score": ps.total_score,
            "matched_areas": ps.matched_areas,
            "in_five_year_plan": in_five_year,
            "in_current_hotspots": in_hotspots,
            "related_sectors": ps.matched_sectors,
            "momentum_bonus": ps.momentum_bonus,
            "level_bonus": ps.level_bonus,
            "max_momentum": max_momentum.value,
            "policy_outlook": outlook,
            "details": ps.details,
            "related_policies": [
                {
                    "name": p["name"],
                    "level": p["level"],
                    "momentum": p["momentum"],
                }
                for p in related_policies
            ],
        }

    # -----------------------------------------------------------------------
    # 关键词匹配
    # -----------------------------------------------------------------------

    def match_policies_by_text(self, text: str) -> List[Dict[str, Any]]:
        """根据文本内容匹配相关政策领域。

        用于分析新闻标题、研报摘要等文本中的政策关联。

        Args:
            text: 待匹配的文本

        Returns:
            匹配到的政策领域列表，按动量排序。
        """
        text_lower = text.lower()
        matched = []

        for name, data in self._all_areas.items():
            keywords = data.get("keywords", [])
            hit_keywords = [kw for kw in keywords if kw in text_lower]

            if hit_keywords:
                mom = data.get("momentum", Momentum.DORMAND)
                lvl = data.get("level", PolicyLevel.GUIDANCE)
                score = MOMENTUM_WEIGHTS.get(mom, 0) + LEVEL_WEIGHTS.get(lvl, 0)

                matched.append({
                    "name": name,
                    "description": data["description"],
                    "level": data["level"].value,
                    "momentum": data["momentum"].value,
                    "hit_keywords": hit_keywords,
                    "match_count": len(hit_keywords),
                    "score": score,
                })

        matched.sort(key=lambda x: (x["match_count"], x["score"]), reverse=True)
        return matched


# ===========================================================================
# 格式化输出
# ===========================================================================

def format_policy_score(score: PolicyScore) -> str:
    """格式化个股政策面评分为可读文本。"""
    lines = [
        "=" * 60,
        f"📋 {score.name}({score.code}) 政策面分析",
        "=" * 60,
        "",
        f"政策面评分: {score.total_score:.1f} / 30",
        f"动量加分: +{score.momentum_bonus:.1f}",
        f"级别加分: +{score.level_bonus:.1f}",
        "",
        f"关联政策领域: {', '.join(score.matched_areas) if score.matched_areas else '无'}",
        f"关联板块: {', '.join(score.matched_sectors) if score.matched_sectors else '无'}",
        "",
        "政策关联详情:",
    ]

    for detail in score.details:
        lines.append(f"  • {detail}")

    if not score.details:
        lines.append("  暂无详细关联信息")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_policy_recommendations(recommendations: List[Dict[str, Any]]) -> str:
    """格式化政策面推荐列表。"""
    lines = [
        "=" * 60,
        "📋 政策面投资推荐",
        "=" * 60,
        "",
    ]

    if not recommendations:
        lines.append("暂无符合条件的推荐标的")
        return "\n".join(lines)

    for i, rec in enumerate(recommendations, 1):
        hotspot_str = ""
        if rec.get("hotspot_tags"):
            hotspot_str = f" 🔥热点: {', '.join(rec['hotspot_tags'])}"

        lines.extend([
            f"{'─' * 50}",
            f"#{i} {rec['name']}({rec['code']})",
            f"  政策分: {rec['policy_score']:.1f}  |  推荐等级: {rec['recommendation_level']}  |  建议: {rec['action']}{hotspot_str}",
            f"  关联领域: {', '.join(rec['matched_areas'])}",
            f"  关联板块: {', '.join(rec['related_sectors'][:5])}",
            "  政策逻辑:",
        ])

        for reason in rec.get("reasons", []):
            lines.append(f"    • {reason}")

    lines.extend([
        "",
        "=" * 60,
        "说明: 政策分满分30，由匹配领域数(×2)+动量加分+级别加分构成",
        "  强烈推荐 ≥ 20分 | 推荐 ≥ 12分 | 关注 ≥ 6分",
        "=" * 60,
    ])

    return "\n".join(lines)


def format_full_analysis(result: Dict[str, Any]) -> str:
    """格式化单只股票完整政策面分析。"""
    lines = [
        "=" * 60,
        f"📋 {result['name']}({result['code']}) 政策面完整分析",
        "=" * 60,
        "",
        f"政策面评分: {result.get('policy_score', 0):.1f} / 30",
        f"最高政策动量: {result.get('max_momentum', '无')}",
        f"政策前景: {result.get('policy_outlook', '未知')}",
        "",
    ]

    # 十四五规划
    fyp = result.get("in_five_year_plan", [])
    if fyp:
        lines.append(f"✅ 十四五规划覆盖: {', '.join(fyp)}")
    else:
        lines.append("⬜ 十四五规划: 未直接覆盖")

    # 当前热点
    hotspots = result.get("in_current_hotspots", [])
    if hotspots:
        lines.append(f"🔥 当前热点: {', '.join(hotspots)}")
    else:
        lines.append("⬜ 当前热点: 未在热点中")

    lines.extend([
        "",
        f"关联板块: {', '.join(result.get('related_sectors', []))}",
        "",
        "政策关联详情:",
    ])

    for detail in result.get("details", []):
        lines.append(f"  • {detail}")

    # 关联政策列表
    related = result.get("related_policies", [])
    if related:
        lines.extend(["", "关联政策领域:"])
        for p in related:
            lines.append(f"  • {p['name']} [{p['level']}] 动量: {p['momentum']}")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_momentum_ranking(ranking: List[Dict[str, Any]]) -> str:
    """格式化政策动量排名。"""
    lines = [
        "=" * 60,
        "📋 政策动量排名",
        "=" * 60,
        "",
    ]

    momentum_emoji = {
        "极强": "🔥🔥🔥",
        "强": "🔥🔥",
        "中等": "🔥",
        "弱": "💤",
        "休眠": "⚫",
    }

    for i, item in enumerate(ranking, 1):
        emoji = momentum_emoji.get(item["momentum"], "")
        lines.append(
            f"  {i:2d}. {emoji} {item['name']}"
            f"  [{item['level']}] 动量: {item['momentum']}"
        )
        lines.append(f"      {item['description']}")

    lines.extend(["", "=" * 60])
    return "\n".join(lines)
