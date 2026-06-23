"""国际局势分析模块 — 全球事件对A股的影响分析。

涵盖：
- 中美关系（贸易战、科技制裁、台海局势）
- 全球经济（美联储政策、欧洲经济、日元套息交易）
- 地缘政治风险（俄乌战争、中东局势、南海问题）
- 全球科技竞争（AI芯片竞赛、量子计算、太空竞争）
- 全球供应链（脱钩回流、友岸外包、关键矿产）
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from loguru import logger


# ===========================================================================
# 枚举与数据类
# ===========================================================================

class RiskLevel(Enum):
    """风险等级。"""
    CRITICAL = "极高风险"
    HIGH = "高风险"
    MODERATE = "中等风险"
    LOW = "低风险"
    MINIMAL = "极低风险"


class TrendDirection(Enum):
    """趋势方向。"""
    ESCALATING = "升级中"
    STABLE = "稳定"
    DEESCALATING = "缓和中"
    UNCERTAIN = "不确定"


class ImpactType(Enum):
    """影响类型。"""
    BENEFICIARY = "受益者"
    VICTIM = "受害者"
    NEUTRAL = "中性"
    MIXED = "混合影响"


@dataclass
class GeopoliticalEvent:
    """地缘政治事件定义。"""
    name: str
    description: str
    category: str
    risk_level: RiskLevel
    trend: TrendDirection
    keywords: List[str]
    beneficiary_sectors: List[str]
    victim_sectors: List[str]
    beneficiary_stocks: List[Dict[str, str]] = field(default_factory=list)
    victim_stocks: List[Dict[str, str]] = field(default_factory=list)
    recent_developments: List[str] = field(default_factory=list)
    impact_magnitude: float = 1.0


@dataclass
class InternationalScore:
    """个股国际局势评分。"""
    code: str
    name: str
    total_score: float
    beneficiary_events: List[str]
    victim_events: List[str]
    risk_exposure: float
    opportunity_score: float
    net_impact: str
    details: List[str] = field(default_factory=list)


# ===========================================================================
# 中美关系事件
# ===========================================================================

US_CHINA_RELATIONS: Dict[str, Dict[str, Any]] = {
    "芯片制裁": {
        "description": "美国对华半导体出口管制，包括先进芯片、设备、EDA工具限制",
        "category": "中美关系",
        "risk_level": RiskLevel.CRITICAL,
        "trend": TrendDirection.ESCALATING,
        "impact_magnitude": 2.0,
        "keywords": [
            "芯片制裁", "半导体管制", "实体清单", "出口管制",
            "chip ban", "entity list", "华为制裁", "SMIC制裁",
            "EDA限制", "光刻机禁运", "ASML", "先进制程",
        ],
        "beneficiary_sectors": [
            "半导体国产替代", "半导体设备", "半导体材料",
            "EDA工具", "国产芯片", "信创",
        ],
        "victim_sectors": [
            "依赖进口芯片企业", "华为供应链受限企业",
        ],
        "beneficiary_stocks": [
            {"code": "688041", "name": "海光信息", "reason": "国产CPU/DCU替代"},
            {"code": "300474", "name": "景嘉微", "reason": "国产GPU替代"},
            {"code": "688256", "name": "寒武纪", "reason": "国产AI芯片"},
            {"code": "688012", "name": "中微公司", "reason": "国产刻蚀设备"},
            {"code": "688019", "name": "安集科技", "reason": "国产CMP材料"},
            {"code": "688072", "name": "拓荆科技", "reason": "国产薄膜设备"},
            {"code": "688037", "name": "芯源微", "reason": "国产涂胶显影"},
            {"code": "300236", "name": "上海新阳", "reason": "国产光刻胶"},
            {"code": "300666", "name": "江丰电子", "reason": "国产靶材"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "美国持续收紧对华芯片出口管制",
            "限制范围扩大至AI芯片和先进封装设备",
            "日本、荷兰跟进限制半导体设备出口",
            "华为被迫发展自主芯片生态",
        ],
    },
    "贸易战": {
        "description": "中美关税战、贸易摩擦、进出口限制",
        "category": "中美关系",
        "risk_level": RiskLevel.HIGH,
        "trend": TrendDirection.UNCERTAIN,
        "impact_magnitude": 1.5,
        "keywords": [
            "贸易战", "关税", "贸易摩擦", "加征关税",
            "trade war", "tariff", "贸易壁垒", "进出口限制",
            "中美贸易", "脱钩", "decoupling",
        ],
        "beneficiary_sectors": [
            "内需消费", "国产替代", "内循环",
        ],
        "victim_sectors": [
            "出口导向企业", "外贸依赖型企业", "跨境电商",
        ],
        "beneficiary_stocks": [
            {"code": "600519", "name": "贵州茅台", "reason": "内需消费龙头"},
            {"code": "000858", "name": "五粮液", "reason": "内需消费"},
            {"code": "000333", "name": "美的集团", "reason": "内需家电+海外产能布局"},
        ],
        "victim_stocks": [
            {"code": "002475", "name": "立讯精密", "reason": "苹果供应链，对美出口"},
            {"code": "300750", "name": "宁德时代", "reason": "北美市场受政策限制"},
        ],
        "recent_developments": [
            "中美关税谈判反复",
            "部分商品关税豁免与恢复交替",
            "企业加速东南亚产能转移",
        ],
    },
    "台海局势": {
        "description": "台湾海峡军事紧张、台独势力挑衅、外部势力干涉",
        "category": "中美关系",
        "risk_level": RiskLevel.HIGH,
        "trend": TrendDirection.UNCERTAIN,
        "impact_magnitude": 1.8,
        "keywords": [
            "台海", "台湾", "台独", "军事演习",
            "Taiwan strait", "台海危机", "两岸关系",
            "对台军售", "海峡中线",
        ],
        "beneficiary_sectors": [
            "军工", "国防", "网络安全", "卫星导航",
        ],
        "victim_sectors": [
            "台海相关出口企业", "航运", "旅游",
        ],
        "beneficiary_stocks": [
            {"code": "600760", "name": "中航沈飞", "reason": "战斗机龙头"},
            {"code": "601989", "name": "中国重工", "reason": "海军装备"},
            {"code": "002049", "name": "紫光国微", "reason": "特种芯片"},
            {"code": "600893", "name": "航发动力", "reason": "航空发动机"},
            {"code": "002179", "name": "中航光电", "reason": "军用连接器"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "解放军台海常态化巡航",
            "美国持续对台军售",
            "台海局势成为A股风险定价因素",
        ],
    },
    "科技脱钩": {
        "description": "中美科技产业链全面脱钩趋势",
        "category": "中美关系",
        "risk_level": RiskLevel.HIGH,
        "trend": TrendDirection.ESCALATING,
        "impact_magnitude": 1.6,
        "keywords": [
            "科技脱钩", "技术封锁", "小院高墙", "技术冷战",
            "tech decoupling", "科技战", "人才封锁",
            "学术交流限制", "投资审查",
        ],
        "beneficiary_sectors": [
            "自主可控", "信创", "国产软件", "国产操作系统",
            "国产数据库", "国产中间件",
        ],
        "victim_sectors": [
            "依赖美国技术的企业", "中美合资企业",
        ],
        "beneficiary_stocks": [
            {"code": "688111", "name": "金山办公", "reason": "国产办公软件"},
            {"code": "600588", "name": "用友网络", "reason": "国产ERP"},
            {"code": "000977", "name": "浪潮信息", "reason": "国产服务器"},
            {"code": "603019", "name": "中科曙光", "reason": "国产高性能计算"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "美国限制对华AI领域投资",
            "中美学术交流收紧",
            "开源社区地缘政治化趋势",
        ],
    },
}


# ===========================================================================
# 全球经济事件
# ===========================================================================

GLOBAL_ECONOMY: Dict[str, Dict[str, Any]] = {
    "美联储加息": {
        "description": "美联储利率政策变动对全球资本流动的影响",
        "category": "全球经济",
        "risk_level": RiskLevel.MODERATE,
        "trend": TrendDirection.UNCERTAIN,
        "impact_magnitude": 1.3,
        "keywords": [
            "美联储", "加息", "降息", "利率", "缩表",
            "Fed", "FOMC", "联邦基金利率", "鸽派", "鹰派",
            "量化宽松", "QE", "QT", "紧缩",
        ],
        "beneficiary_sectors": [
            "黄金", "避险资产",
        ],
        "victim_sectors": [
            "成长股", "高估值科技股", "北向资金重仓股",
        ],
        "beneficiary_stocks": [
            {"code": "600489", "name": "中金黄金", "reason": "黄金避险"},
            {"code": "600547", "name": "山东黄金", "reason": "黄金避险"},
        ],
        "victim_stocks": [
            {"code": "300750", "name": "宁德时代", "reason": "高估值成长股受利率影响"},
            {"code": "688256", "name": "寒武纪", "reason": "高估值科技股"},
        ],
        "recent_developments": [
            "美联储维持高利率时间超预期",
            "降息时点反复推迟",
            "美债收益率高位震荡影响全球风险偏好",
        ],
    },
    "日元套息交易": {
        "description": "日元低利率套息交易平仓对全球风险资产的冲击",
        "category": "全球经济",
        "risk_level": RiskLevel.MODERATE,
        "trend": TrendDirection.UNCERTAIN,
        "impact_magnitude": 1.0,
        "keywords": [
            "日元", "套息交易", "carry trade", "日央行",
            "YCC", "收益率曲线控制", "日元贬值", "日元升值",
            "日本加息",
        ],
        "beneficiary_sectors": [
            "出口日本企业",
        ],
        "victim_sectors": [
            "全球风险资产", "新兴市场",
        ],
        "beneficiary_stocks": [],
        "victim_stocks": [],
        "recent_developments": [
            "日央行结束负利率政策",
            "日元波动引发全球市场震荡",
            "套息交易平仓风险反复出现",
        ],
    },
    "欧洲经济衰退": {
        "description": "欧洲经济放缓、能源危机后遗症、制造业萎缩",
        "category": "全球经济",
        "risk_level": RiskLevel.MODERATE,
        "trend": TrendDirection.STABLE,
        "impact_magnitude": 0.8,
        "keywords": [
            "欧洲经济", "欧元区", "欧央行", "ECB",
            "德国衰退", "欧洲能源危机", "欧洲制造业",
            "欧盟", "欧洲通胀",
        ],
        "beneficiary_sectors": [
            "对欧出口替代企业",
        ],
        "victim_sectors": [
            "对欧出口企业", "欧洲业务占比较高的企业",
        ],
        "beneficiary_stocks": [],
        "victim_stocks": [],
        "recent_developments": [
            "欧元区制造业PMI持续低迷",
            "欧洲央行降息节奏慢于预期",
            "德国经济面临结构性困境",
        ],
    },
    "北向资金波动": {
        "description": "外资通过沪深港通流入流出A股的波动",
        "category": "全球经济",
        "risk_level": RiskLevel.MODERATE,
        "trend": TrendDirection.UNCERTAIN,
        "impact_magnitude": 1.2,
        "keywords": [
            "北向资金", "外资", "QFII", "沪深港通",
            "MSCI", "富时罗素", "外资流出", "外资流入",
            "人民币汇率",
        ],
        "beneficiary_sectors": [
            "外资重仓消费股（汇率稳定时）",
        ],
        "victim_sectors": [
            "外资重仓白马股（外资流出时）",
        ],
        "beneficiary_stocks": [],
        "victim_stocks": [
            {"code": "600519", "name": "贵州茅台", "reason": "外资重仓，受北向资金波动影响"},
            {"code": "000333", "name": "美的集团", "reason": "外资重仓家电股"},
            {"code": "000858", "name": "五粮液", "reason": "外资重仓白酒股"},
        ],
        "recent_developments": [
            "北向资金阶段性大幅流出",
            "人民币汇率贬值压力加大外资流出",
            "MSCI调整成分股影响外资配置",
        ],
    },
}


# ===========================================================================
# 地缘政治风险
# ===========================================================================

GEOPOLITICAL_RISKS: Dict[str, Dict[str, Any]] = {
    "俄乌战争": {
        "description": "俄乌冲突持续对全球能源、粮食、供应链的影响",
        "category": "地缘政治",
        "risk_level": RiskLevel.HIGH,
        "trend": TrendDirection.STABLE,
        "impact_magnitude": 1.2,
        "keywords": [
            "俄乌战争", "俄乌冲突", "Russia", "Ukraine",
            "制裁俄罗斯", "能源危机", "粮食危机",
            "天然气", "石油", "北约", "NATO",
        ],
        "beneficiary_sectors": [
            "能源", "粮食", "军工", "化肥",
        ],
        "victim_sectors": [
            "欧洲业务企业", "受能源价格冲击的制造业",
        ],
        "beneficiary_stocks": [
            {"code": "601857", "name": "中国石油", "reason": "能源价格上涨受益"},
            {"code": "600028", "name": "中国石化", "reason": "能源价格上涨受益"},
            {"code": "601088", "name": "中国神华", "reason": "煤炭价格上涨受益"},
            {"code": "600760", "name": "中航沈飞", "reason": "军工需求增加"},
            {"code": "000998", "name": "隆平高科", "reason": "粮食安全"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "俄乌冲突长期化",
            "欧洲能源结构重塑",
            "全球粮食供应链重组",
        ],
    },
    "中东局势": {
        "description": "中东地区冲突升级对能源供应和航运的影响",
        "category": "地缘政治",
        "risk_level": RiskLevel.HIGH,
        "trend": TrendDirection.ESCALATING,
        "impact_magnitude": 1.3,
        "keywords": [
            "中东", "以色列", "巴勒斯坦", "哈马斯",
            "伊朗", "红海", "胡塞武装", "油价",
            "地缘冲突", "中东战争", "沙特",
            "霍尔木兹海峡", "航运中断",
        ],
        "beneficiary_sectors": [
            "石油石化", "军工", "航运涨价", "黄金避险",
        ],
        "victim_sectors": [
            "远洋运输成本上升企业", "进口依赖型企业",
        ],
        "beneficiary_stocks": [
            {"code": "601857", "name": "中国石油", "reason": "油价上涨受益"},
            {"code": "600028", "name": "中国石化", "reason": "油价上涨受益"},
            {"code": "601989", "name": "中国重工", "reason": "海军装备需求"},
            {"code": "600489", "name": "中金黄金", "reason": "避险需求"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "巴以冲突持续升级",
            "红海航运受胡塞武装袭击",
            "中东局势成为油价波动主要因素",
        ],
    },
    "南海争端": {
        "description": "南海主权争议、域外势力介入、航行自由问题",
        "category": "地缘政治",
        "risk_level": RiskLevel.MODERATE,
        "trend": TrendDirection.UNCERTAIN,
        "impact_magnitude": 1.0,
        "keywords": [
            "南海", "南沙", "菲律宾", "航行自由",
            "南海仲裁", "仁爱礁", "岛礁建设",
            "东盟", "南海争端",
        ],
        "beneficiary_sectors": [
            "军工", "海工装备", "卫星导航",
        ],
        "victim_sectors": [
            "南海航线相关航运企业",
        ],
        "beneficiary_stocks": [
            {"code": "601989", "name": "中国重工", "reason": "海军装备"},
            {"code": "600760", "name": "中航沈飞", "reason": "舰载机"},
            {"code": "002179", "name": "中航光电", "reason": "军用连接器"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "中菲南海摩擦频发",
            "美国强化南海军事存在",
            "南海成为地缘博弈焦点",
        ],
    },
}


# ===========================================================================
# 全球科技竞争
# ===========================================================================

GLOBAL_TECH_COMPETITION: Dict[str, Dict[str, Any]] = {
    "AI芯片竞赛": {
        "description": "全球AI算力芯片军备竞赛，各国争夺AI主导权",
        "category": "科技竞争",
        "risk_level": RiskLevel.LOW,
        "trend": TrendDirection.ESCALATING,
        "impact_magnitude": 1.5,
        "keywords": [
            "AI芯片", "GPU", "算力", "大模型",
            "英伟达", "NVIDIA", "AI训练", "AI推理",
            "算力竞赛", "数据中心", "AI基础设施",
            "H100", "H200", "B200", "GB200",
        ],
        "beneficiary_sectors": [
            "AI芯片", "算力基础设施", "光模块", "AI服务器",
            "液冷散热", "先进封装",
        ],
        "victim_sectors": [],
        "beneficiary_stocks": [
            {"code": "688256", "name": "寒武纪", "reason": "国产AI芯片"},
            {"code": "688041", "name": "海光信息", "reason": "国产AI算力"},
            {"code": "300474", "name": "景嘉微", "reason": "国产GPU"},
            {"code": "000977", "name": "浪潮信息", "reason": "AI服务器龙头"},
            {"code": "603019", "name": "中科曙光", "reason": "高性能计算"},
            {"code": "300308", "name": "中际旭创", "reason": "800G光模块"},
            {"code": "300502", "name": "新易盛", "reason": "高速光模块"},
            {"code": "002185", "name": "华天科技", "reason": "先进封装"},
            {"code": "600584", "name": "长电科技", "reason": "Chiplet封装"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "全球AI算力需求爆发式增长",
            "各国加大AI芯片自主投入",
            "AI芯片成为大国竞争核心战场",
        ],
    },
    "量子计算竞赛": {
        "description": "全球量子计算技术竞争，量子霸权争夺",
        "category": "科技竞争",
        "risk_level": RiskLevel.LOW,
        "trend": TrendDirection.STABLE,
        "impact_magnitude": 0.8,
        "keywords": [
            "量子计算", "量子通信", "量子霸权", "量子芯片",
            "quantum computing", "量子纠缠", "量子密钥",
            "量子卫星", "量子网络",
        ],
        "beneficiary_sectors": [
            "量子计算", "量子通信", "量子安全",
        ],
        "victim_sectors": [],
        "beneficiary_stocks": [
            {"code": "002222", "name": "科华数据", "reason": "量子通信"},
            {"code": "600105", "name": "永鼎股份", "reason": "量子通信光纤"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "中美量子计算竞争加剧",
            "量子纠错技术取得突破",
            "量子计算商业化尚需时日",
        ],
    },
    "太空竞争": {
        "description": "全球太空探索与商业航天竞争",
        "category": "科技竞争",
        "risk_level": RiskLevel.LOW,
        "trend": TrendDirection.ESCALATING,
        "impact_magnitude": 0.7,
        "keywords": [
            "太空", "航天", "卫星", "火箭",
            "星链", "Starlink", "商业航天", "低轨卫星",
            "北斗", "空间站", "月球探测", "火星探测",
            "可回收火箭",
        ],
        "beneficiary_sectors": [
            "航天军工", "卫星制造", "卫星通信",
            "商业航天", "火箭发动机",
        ],
        "victim_sectors": [],
        "beneficiary_stocks": [
            {"code": "600118", "name": "中国卫星", "reason": "卫星制造龙头"},
            {"code": "600879", "name": "航天电子", "reason": "航天电子设备"},
            {"code": "600893", "name": "航发动力", "reason": "火箭发动机"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "中国商业航天快速发展",
            "可回收火箭技术突破",
            "低轨卫星互联网建设加速",
        ],
    },
}


# ===========================================================================
# 全球供应链
# ===========================================================================

GLOBAL_SUPPLY_CHAIN: Dict[str, Dict[str, Any]] = {
    "供应链脱钩": {
        "description": "全球供应链去中国化、产能回流发达国家",
        "category": "供应链",
        "risk_level": RiskLevel.HIGH,
        "trend": TrendDirection.ESCALATING,
        "impact_magnitude": 1.4,
        "keywords": [
            "供应链脱钩", "产能回流", "reshoring", "制造业回流",
            "去中国化", "China+1", "供应链重组",
            "产业转移", "东南亚替代",
        ],
        "beneficiary_sectors": [
            "国产替代", "内循环", "高端制造升级",
        ],
        "victim_sectors": [
            "低端出口制造", "代工企业", "外贸依赖型企业",
        ],
        "beneficiary_stocks": [
            {"code": "300124", "name": "汇川技术", "reason": "工业自动化国产替代"},
            {"code": "002747", "name": "埃斯顿", "reason": "工业机器人国产替代"},
        ],
        "victim_stocks": [
            {"code": "002475", "name": "立讯精密", "reason": "代工企业面临产能转移压力"},
        ],
        "recent_developments": [
            "苹果加速印度、越南产能布局",
            "美国通过芯片法案推动本土制造",
            "中国制造业向高端升级应对",
        ],
    },
    "友岸外包": {
        "description": "西方国家推动供应链向盟友国家转移",
        "category": "供应链",
        "risk_level": RiskLevel.MODERATE,
        "trend": TrendDirection.ESCALATING,
        "impact_magnitude": 1.0,
        "keywords": [
            "友岸外包", "friend-shoring", "近岸外包", "nearshoring",
            "供应链联盟", "印太经济框架", "IPEF",
            "民主供应链",
        ],
        "beneficiary_sectors": [
            "一带一路", "出海东南亚企业", "RCEP受益企业",
        ],
        "victim_sectors": [
            "纯对西方出口企业",
        ],
        "beneficiary_stocks": [
            {"code": "600031", "name": "三一重工", "reason": "工程机械出海"},
            {"code": "601390", "name": "中国中铁", "reason": "一带一路基建"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "美国强化盟友供应链合作",
            "中国企业加速海外产能布局",
            "东南亚成为供应链重组受益地区",
        ],
    },
    "关键矿产争夺": {
        "description": "稀土、锂、钴等关键矿产的全球供应链安全",
        "category": "供应链",
        "risk_level": RiskLevel.MODERATE,
        "trend": TrendDirection.ESCALATING,
        "impact_magnitude": 1.2,
        "keywords": [
            "稀土", "关键矿产", "锂", "钴", "镍",
            "稀土管制", "矿产安全", "资源民族主义",
            "战略资源", "稀有金属", "镓", "锗",
            "锑", "钨",
        ],
        "beneficiary_sectors": [
            "稀土", "稀有金属", "关键矿产",
            "矿产资源", "新能源金属",
        ],
        "victim_sectors": [
            "依赖进口矿产的制造业",
        ],
        "beneficiary_stocks": [
            {"code": "600111", "name": "北方稀土", "reason": "稀土龙头"},
            {"code": "600259", "name": "广晟有色", "reason": "稀土+稀有金属"},
            {"code": "002155", "name": "湖南黄金", "reason": "稀有金属提炼"},
            {"code": "002460", "name": "赣锋锂业", "reason": "锂资源龙头"},
            {"code": "002466", "name": "天齐锂业", "reason": "锂资源"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "中国实施稀土出口管制",
            "镓、锗出口管制引发全球关注",
            "各国加速关键矿产供应链多元化",
        ],
    },
    "能源安全": {
        "description": "全球能源供应安全、石油价格波动、能源转型",
        "category": "供应链",
        "risk_level": RiskLevel.MODERATE,
        "trend": TrendDirection.STABLE,
        "impact_magnitude": 1.1,
        "keywords": [
            "能源安全", "石油", "天然气", "煤炭",
            "能源转型", "新能源", "碳中和",
            "OPEC", "油价", "能源危机",
        ],
        "beneficiary_sectors": [
            "传统能源", "新能源", "储能",
            "能源设备",
        ],
        "victim_sectors": [
            "高能耗制造业",
        ],
        "beneficiary_stocks": [
            {"code": "601857", "name": "中国石油", "reason": "石油龙头"},
            {"code": "601088", "name": "中国神华", "reason": "煤炭龙头"},
            {"code": "300750", "name": "宁德时代", "reason": "储能龙头"},
            {"code": "300274", "name": "阳光电源", "reason": "逆变器+储能"},
        ],
        "victim_stocks": [],
        "recent_developments": [
            "OPEC+减产影响全球油价",
            "中国加速新能源转型",
            "储能技术快速发展",
        ],
    },
}


# ===========================================================================
# 权重配置
# ===========================================================================

RISK_WEIGHTS = {
    RiskLevel.CRITICAL: 4.0,
    RiskLevel.HIGH: 3.0,
    RiskLevel.MODERATE: 2.0,
    RiskLevel.LOW: 1.0,
    RiskLevel.MINIMAL: 0.5,
}

TREND_WEIGHTS = {
    TrendDirection.ESCALATING: 2.0,
    TrendDirection.UNCERTAIN: 1.5,
    TrendDirection.STABLE: 1.0,
    TrendDirection.DEESCALATING: 0.5,
}

MAGNITUDE_MULTIPLIER = {
    "critical": 2.0,
    "high": 1.5,
    "medium": 1.0,
    "low": 0.5,
}


# ===========================================================================
# 国际局势分析器
# ===========================================================================

class InternationalAnalyzer:
    """国际局势对A股影响分析器。

    功能：
    1. 国际事件 → 板块 → 个股映射
    2. 个股国际局势暴露评分
    3. 受益者/受害者识别
    4. 地缘风险预警
    5. 综合投资建议
    """

    def __init__(self):
        self._all_events: Dict[str, Dict[str, Any]] = {}
        self._all_events.update(US_CHINA_RELATIONS)
        self._all_events.update(GLOBAL_ECONOMY)
        self._all_events.update(GEOPOLITICAL_RISKS)
        self._all_events.update(GLOBAL_TECH_COMPETITION)
        self._all_events.update(GLOBAL_SUPPLY_CHAIN)

        self._beneficiary_index: Dict[str, List[str]] = {}
        self._victim_index: Dict[str, List[str]] = {}
        self._sector_index: Dict[str, List[str]] = {}
        self._build_indices()

    def _build_indices(self):
        """构建反向索引。"""
        self._beneficiary_index.clear()
        self._victim_index.clear()
        self._sector_index.clear()

        for event_name, event_data in self._all_events.items():
            for stock in event_data.get("beneficiary_stocks", []):
                code = stock["code"]
                if code not in self._beneficiary_index:
                    self._beneficiary_index[code] = []
                if event_name not in self._beneficiary_index[code]:
                    self._beneficiary_index[code].append(event_name)

            for stock in event_data.get("victim_stocks", []):
                code = stock["code"]
                if code not in self._victim_index:
                    self._victim_index[code] = []
                if event_name not in self._victim_index[code]:
                    self._victim_index[code].append(event_name)

            for sector in event_data.get("beneficiary_sectors", []):
                if sector not in self._sector_index:
                    self._sector_index[sector] = []
                if event_name not in self._sector_index[sector]:
                    self._sector_index[sector].append(event_name)

            for sector in event_data.get("victim_sectors", []):
                key = f"[受害]{sector}"
                if key not in self._sector_index:
                    self._sector_index[key] = []
                if event_name not in self._sector_index[key]:
                    self._sector_index[key].append(event_name)

    # -----------------------------------------------------------------------
    # 查询接口
    # -----------------------------------------------------------------------

    def get_all_events(self) -> List[Dict[str, Any]]:
        """获取所有国际事件概览。"""
        result = []
        for name, data in self._all_events.items():
            result.append({
                "name": name,
                "description": data["description"],
                "category": data["category"],
                "risk_level": data["risk_level"].value,
                "trend": data["trend"].value,
                "beneficiary_count": len(data.get("beneficiary_stocks", [])),
                "victim_count": len(data.get("victim_stocks", [])),
            })
        return result

    def get_events_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按类别获取事件。"""
        result = []
        for name, data in self._all_events.items():
            if data["category"] == category:
                result.append({
                    "name": name,
                    "description": data["description"],
                    "risk_level": data["risk_level"].value,
                    "trend": data["trend"].value,
                    "beneficiary_sectors": data["beneficiary_sectors"],
                    "victim_sectors": data["victim_sectors"],
                    "recent_developments": data.get("recent_developments", []),
                })
        return result

    def get_event_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """按名称获取事件详情。"""
        data = self._all_events.get(name)
        if not data:
            return None
        return {
            "name": name,
            "description": data["description"],
            "category": data["category"],
            "risk_level": data["risk_level"].value,
            "trend": data["trend"].value,
            "impact_magnitude": data["impact_magnitude"],
            "keywords": data["keywords"],
            "beneficiary_sectors": data["beneficiary_sectors"],
            "victim_sectors": data["victim_sectors"],
            "beneficiary_stocks": data.get("beneficiary_stocks", []),
            "victim_stocks": data.get("victim_stocks", []),
            "recent_developments": data.get("recent_developments", []),
        }

    def get_beneficiary_stocks_for_event(self, event_name: str) -> List[Dict[str, str]]:
        """获取事件受益个股。"""
        data = self._all_events.get(event_name)
        if not data:
            return []
        return data.get("beneficiary_stocks", [])

    def get_victim_stocks_for_event(self, event_name: str) -> List[Dict[str, str]]:
        """获取事件受害个股。"""
        data = self._all_events.get(event_name)
        if not data:
            return []
        return data.get("victim_stocks", [])

    def get_events_for_stock(self, code: str) -> Dict[str, List[Dict[str, Any]]]:
        """获取个股关联的所有国际事件（区分受益/受害）。"""
        beneficiary_events = []
        for event_name in self._beneficiary_index.get(code, []):
            event = self.get_event_by_name(event_name)
            if event:
                event["impact_type"] = ImpactType.BENEFICIARY.value
                for stock in self._all_events[event_name].get("beneficiary_stocks", []):
                    if stock["code"] == code:
                        event["reason"] = stock["reason"]
                        break
                beneficiary_events.append(event)

        victim_events = []
        for event_name in self._victim_index.get(code, []):
            event = self.get_event_by_name(event_name)
            if event:
                event["impact_type"] = ImpactType.VICTIM.value
                for stock in self._all_events[event_name].get("victim_stocks", []):
                    if stock["code"] == code:
                        event["reason"] = stock["reason"]
                        break
                victim_events.append(event)

        return {
            "beneficiary_events": beneficiary_events,
            "victim_events": victim_events,
        }

    # -----------------------------------------------------------------------
    # 评分接口
    # -----------------------------------------------------------------------

    def score_stock(self, code: str, name: str = "") -> Optional[InternationalScore]:
        """对单只股票进行国际局势评分。

        评分逻辑：
        - 受益分 = Σ(风险等级权重 × 趋势权重 × 影响幅度) × 受益事件数
        - 受害分 = Σ(风险等级权重 × 趋势权重 × 影响幅度) × 受害事件数
        - 净分 = 受益分 - 受害分
        - 总分上限 30 分
        """
        beneficiary_events = self._beneficiary_index.get(code, [])
        victim_events = self._victim_index.get(code, [])

        if not beneficiary_events and not victim_events:
            return InternationalScore(
                code=code,
                name=name,
                total_score=0.0,
                beneficiary_events=[],
                victim_events=[],
                risk_exposure=0.0,
                opportunity_score=0.0,
                net_impact=ImpactType.NEUTRAL.value,
                details=["未匹配到任何国际事件"],
            )

        opportunity_score = 0.0
        risk_exposure = 0.0
        details = []
        beneficiary_names = []
        victim_names = []

        for event_name in beneficiary_events:
            data = self._all_events.get(event_name)
            if not data:
                continue
            beneficiary_names.append(event_name)

            risk_w = RISK_WEIGHTS.get(data["risk_level"], 1.0)
            trend_w = TREND_WEIGHTS.get(data["trend"], 1.0)
            magnitude = data.get("impact_magnitude", 1.0)
            event_score = risk_w * trend_w * magnitude
            opportunity_score += event_score

            for stock in data.get("beneficiary_stocks", []):
                if stock["code"] == code:
                    details.append(
                        f"【受益·{event_name}】{stock['reason']}"
                        f" (风险:{data['risk_level'].value} 趋势:{data['trend'].value})"
                    )
                    break

        for event_name in victim_events:
            data = self._all_events.get(event_name)
            if not data:
                continue
            victim_names.append(event_name)

            risk_w = RISK_WEIGHTS.get(data["risk_level"], 1.0)
            trend_w = TREND_WEIGHTS.get(data["trend"], 1.0)
            magnitude = data.get("impact_magnitude", 1.0)
            event_score = risk_w * trend_w * magnitude
            risk_exposure += event_score

            for stock in data.get("victim_stocks", []):
                if stock["code"] == code:
                    details.append(
                        f"【风险·{event_name}】{stock['reason']}"
                        f" (风险:{data['risk_level'].value} 趋势:{data['trend'].value})"
                    )
                    break

        net_score = opportunity_score - risk_exposure
        total = max(min(net_score, 30.0), -30.0)

        if net_score > 5:
            net_impact = ImpactType.BENEFICIARY.value
        elif net_score < -5:
            net_impact = ImpactType.VICTIM.value
        elif opportunity_score > 0 and risk_exposure > 0:
            net_impact = ImpactType.MIXED.value
        else:
            net_impact = ImpactType.NEUTRAL.value

        return InternationalScore(
            code=code,
            name=name,
            total_score=round(total, 2),
            beneficiary_events=beneficiary_names,
            victim_events=victim_names,
            risk_exposure=round(risk_exposure, 2),
            opportunity_score=round(opportunity_score, 2),
            net_impact=net_impact,
            details=details,
        )

    def score_stocks(self, stocks: List[Dict[str, Any]]) -> List[InternationalScore]:
        """批量评分。"""
        results = []
        for stock in stocks:
            code = stock.get("code", "")
            name = stock.get("name", "")
            score = self.score_stock(code, name)
            if score and (score.beneficiary_events or score.victim_events):
                results.append(score)

        results.sort(key=lambda x: x.total_score, reverse=True)
        return results

    # -----------------------------------------------------------------------
    # 受益者/受害者识别
    # -----------------------------------------------------------------------

    def identify_beneficiaries(self, event_name: str) -> List[Dict[str, Any]]:
        """识别特定事件的受益者。"""
        data = self._all_events.get(event_name)
        if not data:
            return []

        results = []
        for stock in data.get("beneficiary_stocks", []):
            score = self.score_stock(stock["code"], stock["name"])
            results.append({
                "code": stock["code"],
                "name": stock["name"],
                "reason": stock["reason"],
                "event": event_name,
                "risk_level": data["risk_level"].value,
                "trend": data["trend"].value,
                "international_score": score.total_score if score else 0.0,
            })

        results.sort(key=lambda x: x["international_score"], reverse=True)
        return results

    def identify_victims(self, event_name: str) -> List[Dict[str, Any]]:
        """识别特定事件的受害者。"""
        data = self._all_events.get(event_name)
        if not data:
            return []

        results = []
        for stock in data.get("victim_stocks", []):
            score = self.score_stock(stock["code"], stock["name"])
            results.append({
                "code": stock["code"],
                "name": stock["name"],
                "reason": stock["reason"],
                "event": event_name,
                "risk_level": data["risk_level"].value,
                "trend": data["trend"].value,
                "international_score": score.total_score if score else 0.0,
            })

        results.sort(key=lambda x: x["international_score"])
        return results

    # -----------------------------------------------------------------------
    # 风险预警
    # -----------------------------------------------------------------------

    def get_risk_warnings(self) -> List[Dict[str, Any]]:
        """获取当前国际局势风险预警。"""
        warnings = []

        for name, data in self._all_events.items():
            risk = data["risk_level"]
            trend = data["trend"]

            if risk in (RiskLevel.CRITICAL, RiskLevel.HIGH) and \
               trend in (TrendDirection.ESCALATING, TrendDirection.UNCERTAIN):
                severity = "严重" if risk == RiskLevel.CRITICAL else "警告"

                warnings.append({
                    "event": name,
                    "category": data["category"],
                    "severity": severity,
                    "risk_level": risk.value,
                    "trend": trend.value,
                    "description": data["description"],
                    "affected_sectors": data["beneficiary_sectors"] + data["victim_sectors"],
                    "recent_developments": data.get("recent_developments", []),
                    "recommendation": self._generate_warning_recommendation(data),
                })

        warnings.sort(
            key=lambda x: (
                RISK_WEIGHTS.get(
                    self._all_events[x["event"]]["risk_level"], 0
                ),
                TREND_WEIGHTS.get(
                    self._all_events[x["event"]]["trend"], 0
                ),
            ),
            reverse=True,
        )
        return warnings

    def _generate_warning_recommendation(self, event_data: Dict[str, Any]) -> str:
        """根据事件数据生成风险预警建议。"""
        risk = event_data["risk_level"]
        beneficiary_sectors = event_data.get("beneficiary_sectors", [])
        victim_sectors = event_data.get("victim_sectors", [])

        parts = []
        if risk == RiskLevel.CRITICAL:
            parts.append("高度警惕")
        elif risk == RiskLevel.HIGH:
            parts.append("密切关注")

        if beneficiary_sectors:
            parts.append(f"关注受益板块: {', '.join(beneficiary_sectors[:3])}")
        if victim_sectors:
            parts.append(f"规避风险板块: {', '.join(victim_sectors[:3])}")

        return "；".join(parts) if parts else "保持关注"

    # -----------------------------------------------------------------------
    # 综合分析
    # -----------------------------------------------------------------------

    def full_analysis(self, stock_code: str, stock_name: str = "") -> Dict[str, Any]:
        """对单只股票进行完整的国际局势分析。"""
        score = self.score_stock(stock_code, stock_name)
        if not score:
            return {
                "code": stock_code,
                "name": stock_name,
                "error": "无法评分",
            }

        events = self.get_events_for_stock(stock_code)

        categories_hit: Dict[str, List[str]] = {}
        for event in events["beneficiary_events"]:
            cat = event["category"]
            if cat not in categories_hit:
                categories_hit[cat] = []
            categories_hit[cat].append(f"受益:{event['name']}")
        for event in events["victim_events"]:
            cat = event["category"]
            if cat not in categories_hit:
                categories_hit[cat] = []
            categories_hit[cat].append(f"风险:{event['name']}")

        if score.total_score > 10:
            outlook = "国际局势高度利好，显著受益于当前全球格局"
        elif score.total_score > 5:
            outlook = "国际局势偏利好，有一定受益空间"
        elif score.total_score > 0:
            outlook = "国际局势轻微利好"
        elif score.total_score > -5:
            outlook = "国际局势影响中性"
        elif score.total_score > -10:
            outlook = "国际局势偏利空，存在一定风险"
        else:
            outlook = "国际局势高度利空，需谨慎对待"

        return {
            "code": stock_code,
            "name": stock_name,
            "international_score": score.total_score,
            "net_impact": score.net_impact,
            "opportunity_score": score.opportunity_score,
            "risk_exposure": score.risk_exposure,
            "beneficiary_events": [e["name"] for e in events["beneficiary_events"]],
            "victim_events": [e["name"] for e in events["victim_events"]],
            "categories_hit": categories_hit,
            "international_outlook": outlook,
            "details": score.details,
            "event_details": {
                "beneficiary": [
                    {
                        "name": e["name"],
                        "category": e["category"],
                        "risk_level": e["risk_level"],
                        "trend": e["trend"],
                        "reason": e.get("reason", ""),
                    }
                    for e in events["beneficiary_events"]
                ],
                "victim": [
                    {
                        "name": e["name"],
                        "category": e["category"],
                        "risk_level": e["risk_level"],
                        "trend": e["trend"],
                        "reason": e.get("reason", ""),
                    }
                    for e in events["victim_events"]
                ],
            },
        }

    # -----------------------------------------------------------------------
    # 关键词匹配
    # -----------------------------------------------------------------------

    def match_events_by_text(self, text: str) -> List[Dict[str, Any]]:
        """根据文本内容匹配相关国际事件。"""
        text_lower = text.lower()
        matched = []

        for name, data in self._all_events.items():
            keywords = data.get("keywords", [])
            hit_keywords = [kw for kw in keywords if kw in text_lower]

            if hit_keywords:
                risk_w = RISK_WEIGHTS.get(data["risk_level"], 0)
                trend_w = TREND_WEIGHTS.get(data["trend"], 0)
                score = risk_w * trend_w * data.get("impact_magnitude", 1.0)

                matched.append({
                    "name": name,
                    "description": data["description"],
                    "category": data["category"],
                    "risk_level": data["risk_level"].value,
                    "trend": data["trend"].value,
                    "hit_keywords": hit_keywords,
                    "match_count": len(hit_keywords),
                    "score": score,
                })

        matched.sort(key=lambda x: (x["match_count"], x["score"]), reverse=True)
        return matched

    # -----------------------------------------------------------------------
    # 投资建议
    # -----------------------------------------------------------------------

    def generate_recommendations(
        self,
        top_n: int = 10,
        min_score: float = 3.0,
    ) -> List[Dict[str, Any]]:
        """生成国际局势面投资建议。"""
        all_targets: Dict[str, Dict[str, str]] = {}
        for data in self._all_events.values():
            for target in data.get("beneficiary_stocks", []):
                code = target["code"]
                if code not in all_targets:
                    all_targets[code] = target

        scores = self.score_stocks(list(all_targets.values()))
        filtered = [s for s in scores if s.total_score >= min_score]

        recommendations = []
        for ps in filtered[:top_n]:
            if ps.total_score >= 15:
                level = "强烈推荐"
                action = "重点关注"
            elif ps.total_score >= 8:
                level = "推荐"
                action = "适当配置"
            elif ps.total_score >= 3:
                level = "关注"
                action = "纳入观察"
            else:
                level = "一般"
                action = "暂不操作"

            recommendations.append({
                "code": ps.code,
                "name": ps.name,
                "international_score": ps.total_score,
                "recommendation_level": level,
                "action": action,
                "net_impact": ps.net_impact,
                "opportunity_score": ps.opportunity_score,
                "risk_exposure": ps.risk_exposure,
                "beneficiary_events": ps.beneficiary_events,
                "victim_events": ps.victim_events,
                "reasons": ps.details,
            })

        return recommendations

    # -----------------------------------------------------------------------
    # 全球格局概览
    # -----------------------------------------------------------------------

    def get_global_overview(self) -> Dict[str, Any]:
        """获取当前全球格局概览。"""
        categories = {
            "中美关系": US_CHINA_RELATIONS,
            "全球经济": GLOBAL_ECONOMY,
            "地缘政治": GEOPOLITICAL_RISKS,
            "科技竞争": GLOBAL_TECH_COMPETITION,
            "供应链": GLOBAL_SUPPLY_CHAIN,
        }

        overview = {}
        for cat_name, cat_data in categories.items():
            events = []
            total_risk = 0.0
            for name, data in cat_data.items():
                risk_w = RISK_WEIGHTS.get(data["risk_level"], 0)
                trend_w = TREND_WEIGHTS.get(data["trend"], 0)
                event_risk = risk_w * trend_w * data.get("impact_magnitude", 1.0)
                total_risk += event_risk
                events.append({
                    "name": name,
                    "risk_level": data["risk_level"].value,
                    "trend": data["trend"].value,
                    "event_risk": round(event_risk, 2),
                })

            if total_risk >= 20:
                cat_assessment = "高危"
            elif total_risk >= 10:
                cat_assessment = "警戒"
            elif total_risk >= 5:
                cat_assessment = "关注"
            else:
                cat_assessment = "平稳"

            overview[cat_name] = {
                "assessment": cat_assessment,
                "total_risk": round(total_risk, 2),
                "event_count": len(events),
                "events": sorted(events, key=lambda x: x["event_risk"], reverse=True),
            }

        total_global_risk = sum(v["total_risk"] for v in overview.values())
        if total_global_risk >= 50:
            global_assessment = "极高风险"
        elif total_global_risk >= 30:
            global_assessment = "高风险"
        elif total_global_risk >= 15:
            global_assessment = "中等风险"
        else:
            global_assessment = "低风险"

        return {
            "global_assessment": global_assessment,
            "total_global_risk": round(total_global_risk, 2),
            "categories": overview,
            "active_warnings": len(self.get_risk_warnings()),
            "timestamp": datetime.now().isoformat(),
        }


# ===========================================================================
# 格式化输出
# ===========================================================================

def format_international_score(score: InternationalScore) -> str:
    """格式化个股国际局势评分为可读文本。"""
    lines = [
        "=" * 60,
        f"🌍 {score.name}({score.code}) 国际局势分析",
        "=" * 60,
        "",
        f"国际局势评分: {score.total_score:.1f} / 30",
        f"机会得分: {score.opportunity_score:.1f}",
        f"风险暴露: {score.risk_exposure:.1f}",
        f"净影响: {score.net_impact}",
        "",
        f"受益事件: {', '.join(score.beneficiary_events) if score.beneficiary_events else '无'}",
        f"风险事件: {', '.join(score.victim_events) if score.victim_events else '无'}",
        "",
        "事件关联详情:",
    ]

    for detail in score.details:
        lines.append(f"  • {detail}")

    if not score.details:
        lines.append("  暂无详细关联信息")

    lines.append("=" * 60)
    return "\n".join(lines)


def format_risk_warnings(warnings: List[Dict[str, Any]]) -> str:
    """格式化风险预警。"""
    lines = [
        "=" * 60,
        "⚠️ 国际局势风险预警",
        "=" * 60,
        "",
    ]

    if not warnings:
        lines.append("当前无高风险预警")
        return "\n".join(lines)

    severity_emoji = {"严重": "🔴", "警告": "🟡"}

    for w in warnings:
        emoji = severity_emoji.get(w["severity"], "⚪")
        lines.extend([
            f"{'─' * 50}",
            f"{emoji} [{w['severity']}] {w['event']}",
            f"  类别: {w['category']}  |  风险: {w['risk_level']}  |  趋势: {w['trend']}",
            f"  说明: {w['description']}",
            f"  建议: {w['recommendation']}",
        ])

        if w.get("affected_sectors"):
            lines.append(f"  涉及板块: {', '.join(w['affected_sectors'][:5])}")

        if w.get("recent_developments"):
            lines.append("  最新动态:")
            for dev in w["recent_developments"][:3]:
                lines.append(f"    • {dev}")

    lines.extend(["", "=" * 60])
    return "\n".join(lines)


def format_global_overview(overview: Dict[str, Any]) -> str:
    """格式化全球格局概览。"""
    lines = [
        "=" * 60,
        "🌍 全球格局概览",
        "=" * 60,
        "",
        f"综合评估: {overview['global_assessment']}",
        f"全球风险指数: {overview['total_global_risk']:.1f}",
        f"活跃预警数: {overview['active_warnings']}",
        "",
    ]

    assessment_emoji = {
        "高危": "🔴",
        "警戒": "🟡",
        "关注": "🟠",
        "平稳": "🟢",
    }

    for cat_name, cat_data in overview["categories"].items():
        emoji = assessment_emoji.get(cat_data["assessment"], "⚪")
        lines.extend([
            f"{'─' * 50}",
            f"{emoji} {cat_name} [{cat_data['assessment']}]",
            f"  风险指数: {cat_data['total_risk']:.1f}  |  事件数: {cat_data['event_count']}",
        ])

        for event in cat_data["events"][:3]:
            lines.append(
                f"  • {event['name']} — 风险:{event['risk_level']} "
                f"趋势:{event['trend']} 指数:{event['event_risk']:.1f}"
            )

    lines.extend(["", "=" * 60])
    return "\n".join(lines)


def format_recommendations(recommendations: List[Dict[str, Any]]) -> str:
    """格式化投资推荐。"""
    lines = [
        "=" * 60,
        "🌍 国际局势面投资推荐",
        "=" * 60,
        "",
    ]

    if not recommendations:
        lines.append("暂无符合条件的推荐标的")
        return "\n".join(lines)

    for i, rec in enumerate(recommendations, 1):
        lines.extend([
            f"{'─' * 50}",
            f"#{i} {rec['name']}({rec['code']})",
            f"  评分: {rec['international_score']:.1f}  |  等级: {rec['recommendation_level']}  "
            f"|  建议: {rec['action']}",
            f"  净影响: {rec['net_impact']}  |  机会分: {rec['opportunity_score']:.1f}  "
            f"|  风险暴露: {rec['risk_exposure']:.1f}",
        ])

        if rec.get("beneficiary_events"):
            lines.append(f"  受益事件: {', '.join(rec['beneficiary_events'])}")
        if rec.get("victim_events"):
            lines.append(f"  风险事件: {', '.join(rec['victim_events'])}")

        lines.append("  评分逻辑:")
        for reason in rec.get("reasons", []):
            lines.append(f"    • {reason}")

    lines.extend([
        "",
        "=" * 60,
        "说明: 评分 = 机会得分 - 风险暴露，满分±30",
        "  强烈推荐 ≥ 15分 | 推荐 ≥ 8分 | 关注 ≥ 3分",
        "=" * 60,
    ])

    return "\n".join(lines)


def format_full_analysis(result: Dict[str, Any]) -> str:
    """格式化完整国际局势分析。"""
    lines = [
        "=" * 60,
        f"🌍 {result['name']}({result['code']}) 国际局势完整分析",
        "=" * 60,
        "",
        f"国际局势评分: {result.get('international_score', 0):.1f} / 30",
        f"净影响: {result.get('net_impact', '未知')}",
        f"国际局势前景: {result.get('international_outlook', '未知')}",
        "",
        f"机会得分: {result.get('opportunity_score', 0):.1f}",
        f"风险暴露: {result.get('risk_exposure', 0):.1f}",
        "",
    ]

    beneficiary = result.get("beneficiary_events", [])
    if beneficiary:
        lines.append(f"✅ 受益事件: {', '.join(beneficiary)}")
    else:
        lines.append("⬜ 受益事件: 无")

    victim = result.get("victim_events", [])
    if victim:
        lines.append(f"⚠️ 风险事件: {', '.join(victim)}")
    else:
        lines.append("⬜ 风险事件: 无")

    categories = result.get("categories_hit", {})
    if categories:
        lines.extend(["", "影响类别:"])
        for cat, events in categories.items():
            lines.append(f"  • {cat}: {', '.join(events)}")

    lines.extend(["", "事件关联详情:"])
    for detail in result.get("details", []):
        lines.append(f"  • {detail}")

    if not result.get("details"):
        lines.append("  暂无详细关联信息")

    lines.append("=" * 60)
    return "\n".join(lines)
