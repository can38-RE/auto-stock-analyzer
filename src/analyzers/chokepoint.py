"""Serenity-style Chokepoint Theory Analyzer for A-share AI/semiconductor stocks.

Based on @aleabitoreddit's framework:
- "Own the bottleneck, not the brand"
- Find single-vendor/duopoly chokepoints in AI supply chain
- Focus on physical switches, not chip design houses
"""

from typing import List, Dict, Any
from loguru import logger


class ChokepointAnalyzer:
    """Analyze stocks using Serenity's Chokepoint Theory."""
    
    # A股AI供应链瓶颈映射
    CHOKEPOINT_MAP = {
        # Layer 1: 原材料 - 镓、铟、砷
        "raw_materials": {
            "description": "稀有金属原材料（镓、铟、砷）",
            "importance": "critical",
            "a_share_targets": [
                {"code": "002155", "name": "湖南黄金", "reason": "稀有金属提炼"},
                {"code": "600259", "name": "广晟有色", "reason": "稀土+稀有金属"},
                {"code": "000975", "name": "银泰黄金", "reason": "贵金属+稀有金属"},
                {"code": "600111", "name": "北方稀土", "reason": "稀土龙头"},
            ]
        },
        
        # Layer 2: 半导体材料 - 光刻胶、靶材、抛光液
        "semiconductor_materials": {
            "description": "半导体关键材料",
            "importance": "critical",
            "a_share_targets": [
                {"code": "688019", "name": "安集科技", "reason": "CMP抛光液龙头"},
                {"code": "300236", "name": "上海新阳", "reason": "光刻胶+电镀液"},
                {"code": "300666", "name": "江丰电子", "reason": "高纯溅射靶材"},
                {"code": "300346", "name": "南大光电", "reason": "ArF光刻胶"},
                {"code": "688035", "name": "德邦科技", "reason": "半导体封装材料"},
            ]
        },
        
        # Layer 3: 先进封装 - CoWoS、HBM
        "advanced_packaging": {
            "description": "先进封装技术（CoWoS、HBM）",
            "importance": "critical",
            "a_share_targets": [
                {"code": "002185", "name": "华天科技", "reason": "先进封装产能"},
                {"code": "600584", "name": "长电科技", "reason": "Chiplet封装"},
                {"code": "002049", "name": "紫光国微", "reason": "HBM相关芯片"},
            ]
        },
        
        # Layer 4: 光模块/光通信 - CPO
        "optical_communication": {
            "description": "光模块、共封装光学（CPO）",
            "importance": "high",
            "a_share_targets": [
                {"code": "300308", "name": "中际旭创", "reason": "800G光模块龙头"},
                {"code": "002281", "name": "兴迅科技", "reason": "光通信器件"},
                {"code": "300548", "name": "博创科技", "reason": "PLC分路器"},
                {"code": "300502", "name": "新易盛", "reason": "高速光模块"},
                {"code": "002396", "name": "星网锐捷", "reason": "网络设备+光通信"},
            ]
        },
        
        # Layer 5: AI芯片设计
        "ai_chips": {
            "description": "AI芯片设计",
            "importance": "high",
            "a_share_targets": [
                {"code": "688256", "name": "寒武纪", "reason": "AI推理芯片"},
                {"code": "688041", "name": "海光信息", "reason": "国产CPU/DCU"},
                {"code": "300474", "name": "景嘉微", "reason": "国产GPU"},
            ]
        },
        
        # Layer 6: 设备 - 光刻机、刻蚀机
        "equipment": {
            "description": "半导体设备",
            "importance": "critical",
            "a_share_targets": [
                {"code": "688012", "name": "中微公司", "reason": "刻蚀设备龙头"},
                {"code": "688037", "name": "芯源微", "reason": "涂胶显影设备"},
                {"code": "688072", "name": "拓荆科技", "reason": "薄膜沉积设备"},
                {"code": "300236", "name": "上海新阳", "reason": "清洗设备"},
            ]
        },
        
        # Layer 7: 算力基础设施
        "infrastructure": {
            "description": "算力基础设施（服务器、液冷）",
            "importance": "medium",
            "a_share_targets": [
                {"code": "000977", "name": "浪潮信息", "reason": "AI服务器龙头"},
                {"code": "603019", "name": "中科曙光", "reason": "高性能计算"},
                {"code": "002281", "name": "兴迅科技", "reason": "光通信+算力"},
            ]
        },
    }
    
    # 三阶段轮动
    ROTATION_PHASES = {
        "phase1_memory_hbm": {
            "status": "completed",
            "description": "内存/HBM - 机构已入场",
            "stocks": ["002049", "688981"],  # 紫光国微、中芯国际
        },
        "phase2_optical_transceiver": {
            "status": "current",
            "description": "光收发器 - 当前主战场",
            "stocks": ["300308", "002281", "300548", "300502"],  # 中际旭创、兴迅科技、博创科技、新易盛
        },
        "phase3_siph_cpo": {
            "status": "emerging",
            "description": "硅光/CPO - 2027-2028拐点",
            "stocks": ["002281", "300548"],  # 兴迅科技、博创科技
        },
    }
    
    def analyze_stock(self, code: str) -> Dict[str, Any] | None:
        """Check if a stock is in the chokepoint map."""
        for layer, data in self.CHOKEPOINT_MAP.items():
            for target in data["a_share_targets"]:
                if target["code"] == code:
                    return {
                        "code": code,
                        "name": target["name"],
                        "layer": layer,
                        "layer_description": data["description"],
                        "importance": data["importance"],
                        "reason": target["reason"],
                        "is_chokepoint": True,
                    }
        return None
    
    def get_chokepoint_stocks(self, affordable_only: bool = True, 
                              budget: float = 1900) -> List[Dict[str, Any]]:
        """Get all chokepoint stocks, optionally filtered by affordability."""
        stocks = []
        
        for layer, data in self.CHOKEPOINT_MAP.items():
            for target in data["a_share_targets"]:
                stock = {
                    "code": target["code"],
                    "name": target["name"],
                    "layer": layer,
                    "layer_description": data["description"],
                    "importance": data["importance"],
                    "reason": target["reason"],
                    "is_chokepoint": True,
                }
                stocks.append(stock)
        
        # Remove duplicates (some stocks appear in multiple layers)
        seen = set()
        unique_stocks = []
        for s in stocks:
            if s["code"] not in seen:
                seen.add(s["code"])
                unique_stocks.append(s)
        
        return unique_stocks
    
    def get_current_phase_stocks(self) -> List[str]:
        """Get stocks in the current rotation phase."""
        return self.ROTATION_PHASES["phase2_optical_transceiver"]["stocks"]
    
    def get_emerging_phase_stocks(self) -> List[str]:
        """Get stocks in the emerging rotation phase."""
        return self.ROTATION_PHASES["phase3_siph_cpo"]["stocks"]
    
    def generate_insight(self, stock_code: str) -> str:
        """Generate Serenity-style insight for a stock."""
        analysis = self.analyze_stock(stock_code)
        if not analysis:
            return f"{stock_code} 不在瓶颈图谱中"
        
        importance_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡"}
        emoji = importance_emoji.get(analysis["importance"], "⚪")
        
        insight = f"{emoji} 【瓶颈分析】{analysis['name']}({analysis['code']})\n"
        insight += f"供应链位置: {analysis['layer_description']}\n"
        insight += f"瓶颈等级: {analysis['importance']}\n"
        insight += f"核心逻辑: {analysis['reason']}\n"
        insight += f"Serenity框架: 'Own the bottleneck, not the brand'"
        
        return insight


def format_chokepoint_analysis(stocks: List[Dict[str, Any]]) -> str:
    """Format chokepoint analysis as readable text."""
    lines = [
        "=" * 60,
        "🎯 Serenity瓶颈理论分析",
        "=" * 60,
        "",
        "核心理念: 'Own the bottleneck, not the brand'",
        "寻找AI供应链中不可替代的瓶颈环节",
        "",
        "供应链瓶颈图谱:",
        "-" * 60,
    ]
    
    # Group by layer
    layers = {}
    for stock in stocks:
        layer = stock.get("layer", "unknown")
        if layer not in layers:
            layers[layer] = []
        layers[layer].append(stock)
    
    layer_names = {
        "raw_materials": "🔴 Layer 1: 原材料",
        "semiconductor_materials": "🔴 Layer 2: 半导体材料",
        "advanced_packaging": "🔴 Layer 3: 先进封装",
        "optical_communication": "🟠 Layer 4: 光通信/CPO",
        "ai_chips": "🟠 Layer 5: AI芯片",
        "equipment": "🔴 Layer 6: 半导体设备",
        "infrastructure": "🟡 Layer 7: 算力基础设施",
    }
    
    for layer, name in layer_names.items():
        if layer in layers:
            lines.append(f"\n{name}")
            for s in layers[layer]:
                lines.append(f"  {s['code']} {s['name']} - {s['reason']}")
    
    lines.extend([
        "",
        "=" * 60,
        "三阶段轮动策略:",
        "  Phase 1 (已完成): 内存/HBM",
        "  Phase 2 (当前): 光收发器 ← 当前主战场",
        "  Phase 3 (新兴): SiPh/CPO ← 2027-2028拐点",
        "=" * 60,
    ])
    
    return "\n".join(lines)
