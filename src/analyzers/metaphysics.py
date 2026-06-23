"""Chinese Metaphysics Analysis Module (玄学分析).

Incorporates traditional Chinese metaphysical concepts:
- 周易 (I Ching / Book of Changes)
- 黄历 (Chinese Almanac)
- 五行 (Five Elements)
- 风水方位 (Feng Shui directions)

Disclaimer: This is for entertainment/cultural reference only, not financial advice.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List
from loguru import logger


class MetaphysicsAnalyzer:
    """Analyze stocks using Chinese metaphysical concepts."""
    
    # 天干 (Heavenly Stems)
    TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    
    # 地支 (Earthly Branches)
    DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    # 五行对应 (Five Elements)
    WUXING = {
        "甲": "木", "乙": "木",
        "丙": "火", "丁": "火",
        "戊": "土", "己": "土",
        "庚": "金", "辛": "金",
        "壬": "水", "癸": "水",
        "子": "水", "丑": "土", "寅": "木", "卯": "木",
        "辰": "土", "巳": "火", "午": "火", "未": "土",
        "申": "金", "酉": "金", "戌": "土", "亥": "水"
    }
    
    # 五行相生 (Generation)
    WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
    
    # 五行相克 (Overcoming)
    WUXING_KE = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
    
    # 行业五行属性
    SECTOR_WUXING = {
        "金融": "金",
        "银行": "金",
        "证券": "金",
        "保险": "金",
        "科技": "火",
        "电子": "火",
        "互联网": "火",
        "人工智能": "火",
        "消费": "土",
        "食品": "土",
        "白酒": "土",
        "地产": "土",
        "医药": "木",
        "医疗": "木",
        "新能源": "木",
        "环保": "木",
        "水利": "水",
        "航运": "水",
        "传媒": "水",
        "物流": "水",
    }
    
    # 黄历宜忌
    YI_ITEMS = {
        "开市": "适合开仓买入",
        "交易": "适合交易",
        "纳财": "适合投资",
        "投资": "适合投资",
        "签约": "适合建仓",
    }
    
    JI_ITEMS = {
        "破土": "不宜大动作",
        "安葬": "不宜买入",
        "诉讼": "注意风险",
        "出行": "波动较大",
    }
    
    def __init__(self):
        """Initialize metaphysics analyzer."""
        self.today = datetime.now()
    
    def get_ganzhi(self, date: datetime = None) -> Dict[str, str]:
        """Get 干支 (Heavenly Stems and Earthly Branches) for a date.
        
        Args:
            date: Date to analyze
            
        Returns:
            Dictionary with year, month, day 干支
        """
        if date is None:
            date = self.today
        
        # Simplified calculation (for demonstration)
        # Real calculation is more complex
        year = date.year
        month = date.month
        day = date.day
        
        # Year 干支 (based on Chinese calendar)
        year_gan = self.TIANGAN[(year - 4) % 10]
        year_zhi = self.DIZHI[(year - 4) % 12]
        
        # Month 干支 (simplified)
        month_gan = self.TIANGAN[(year * 12 + month - 1) % 10]
        month_zhi = self.DIZHI[(month + 1) % 12]
        
        # Day 干支 (simplified - use Julian day number)
        julian_day = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day - 1524.5
        day_gan = self.TIANGAN[int(julian_day) % 10]
        day_zhi = self.DIZHI[int(julian_day) % 12]
        
        return {
            "year": f"{year_gan}{year_zhi}",
            "month": f"{month_gan}{month_zhi}",
            "day": f"{day_gan}{day_zhi}",
            "year_wuxing": self.WUXING[year_gan],
            "month_wuxing": self.WUXING[month_gan],
            "day_wuxing": self.WUXING[day_gan],
        }
    
    def analyze_day_fortune(self, date: datetime = None) -> Dict[str, Any]:
        """Analyze if today is good for trading.
        
        Args:
            date: Date to analyze
            
        Returns:
            Fortune analysis
        """
        ganzhi = self.get_ganzhi(date)
        
        # Determine day element
        day_element = ganzhi["day_wuxing"]
        
        # Calculate trading fortune based on 五行
        fortune_score = 50  # Base score
        
        # Day element analysis
        element_fortune = {
            "金": {"score": 65, "desc": "金日主收敛，适合观望", "action": "谨慎"},
            "木": {"score": 70, "desc": "木日主生长，适合买入", "action": "积极"},
            "火": {"score": 60, "desc": "火日主热情，市场活跃", "action": "跟随"},
            "土": {"score": 55, "desc": "土日主稳定，适合持有", "action": "观望"},
            "水": {"score": 75, "desc": "水日主流动，资金活跃", "action": "积极"},
        }
        
        day_fortune = element_fortune.get(day_element, {"score": 50, "desc": "中性", "action": "观望"})
        
        # Check 相生相克
        sheng_element = self.WUXING_SHENG.get(day_element)
        ke_element = self.WUXING_KE.get(day_element)
        
        # Determine favorable sectors
        favorable_sectors = []
        unfavorable_sectors = []
        
        for sector, element in self.SECTOR_WUXING.items():
            if element == day_element or element == sheng_element:
                favorable_sectors.append(sector)
            elif element == ke_element:
                unfavorable_sectors.append(sector)
        
        # Calculate overall score
        fortune_score = day_fortune["score"]
        
        # Add some randomness based on date (for variety)
        date_seed = date.day + date.month * 31
        fortune_score += (date_seed % 10) - 5
        
        return {
            "date": date.strftime("%Y-%m-%d"),
            "ganzhi": ganzhi,
            "day_element": day_element,
            "fortune_score": fortune_score,
            "fortune_desc": day_fortune["desc"],
            "action": day_fortune["action"],
            "favorable_sectors": favorable_sectors[:5],
            "unfavorable_sectors": unfavorable_sectors[:5],
            "yi": ["交易", "开市"] if fortune_score > 60 else ["观望"],
            "ji": ["追高", "满仓"] if fortune_score < 60 else ["恐慌"],
        }
    
    def analyze_stock_metaphysics(self, code: str, name: str, 
                                   sector: str = "") -> Dict[str, Any]:
        """Analyze a stock using metaphysical concepts.
        
        Args:
            code: Stock code
            name: Stock name
            sector: Stock sector
            
        Returns:
            Metaphysical analysis
        """
        # Get stock's 五行 attribute
        stock_element = self._get_stock_element(code, name, sector)
        
        # Get today's fortune
        day_fortune = self.analyze_day_fortune()
        day_element = day_fortune["day_element"]
        
        # Calculate compatibility
        compatibility = self._calculate_compatibility(stock_element, day_element)
        
        # Calculate metaphysical score
        meta_score = 50
        
        # Element compatibility
        if compatibility["relationship"] == "相生":
            meta_score += 20
        elif compatibility["relationship"] == "相同":
            meta_score += 10
        elif compatibility["relationship"] == "相克":
            meta_score -= 15
        
        # Sector favorability
        if sector in day_fortune["favorable_sectors"]:
            meta_score += 15
        elif sector in day_fortune["unfavorable_sectors"]:
            meta_score -= 10
        
        # Number analysis (based on stock code)
        code_score = self._analyze_code_numbers(code)
        meta_score += code_score
        
        # Direction analysis (based on code last digit)
        direction = self._get_fengshui_direction(code)
        
        return {
            "code": code,
            "name": name,
            "stock_element": stock_element,
            "day_element": day_element,
            "compatibility": compatibility,
            "meta_score": min(max(meta_score, 0), 100),
            "direction": direction,
            "advice": self._generate_metaphysical_advice(meta_score, compatibility),
        }
    
    def _get_stock_element(self, code: str, name: str, sector: str) -> str:
        """Get stock's 五行 attribute."""
        # Check sector first
        for sec, element in self.SECTOR_WUXING.items():
            if sec in sector or sec in name:
                return element
        
        # Based on code number
        last_digit = int(code[-1]) if code[-1].isdigit() else 0
        element_by_number = {
            0: "水", 1: "木", 2: "木", 3: "火", 4: "火",
            5: "土", 6: "土", 7: "金", 8: "金", 9: "水"
        }
        
        return element_by_number.get(last_digit, "土")
    
    def _calculate_compatibility(self, element1: str, element2: str) -> Dict[str, Any]:
        """Calculate compatibility between two elements."""
        if element1 == element2:
            return {
                "relationship": "相同",
                "desc": f"{element1}与{element2}同属，和谐",
                "score": 10
            }
        
        if self.WUXING_SHENG.get(element1) == element2:
            return {
                "relationship": "相生",
                "desc": f"{element1}生{element2}，有利",
                "score": 20
            }
        
        if self.WUXING_SHENG.get(element2) == element1:
            return {
                "relationship": "相生",
                "desc": f"{element2}生{element1}，有利",
                "score": 15
            }
        
        if self.WUXING_KE.get(element1) == element2:
            return {
                "relationship": "相克",
                "desc": f"{element1}克{element2}，不利",
                "score": -15
            }
        
        if self.WUXING_KE.get(element2) == element1:
            return {
                "relationship": "相克",
                "desc": f"{element2}克{element1}，不利",
                "score": -10
            }
        
        return {
            "relationship": "中性",
            "desc": "无特殊关系",
            "score": 0
        }
    
    def _analyze_code_numbers(self, code: str) -> int:
        """Analyze stock code numbers for fortune."""
        score = 0
        
        # Lucky numbers in Chinese culture
        lucky_numbers = {6, 8, 9}
        unlucky_numbers = {4}
        
        for char in code:
            if char.isdigit():
                num = int(char)
                if num in lucky_numbers:
                    score += 2
                elif num in unlucky_numbers:
                    score -= 2
        
        # Consecutive numbers (like 666, 888)
        if len(set(code[-3:])) == 1:
            digit = int(code[-1])
            if digit in lucky_numbers:
                score += 10
        
        return score
    
    def _get_fengshui_direction(self, code: str) -> Dict[str, str]:
        """Get feng shui direction based on code."""
        last_digit = int(code[-1]) if code[-1].isdigit() else 0
        
        directions = {
            0: {"direction": "北方", "element": "水", "advice": "北方属水，利流动"},
            1: {"direction": "东方", "element": "木", "advice": "东方属木，利生长"},
            2: {"direction": "东方", "element": "木", "advice": "东方属木，利生长"},
            3: {"direction": "南方", "element": "火", "advice": "南方属火，利热情"},
            4: {"direction": "南方", "element": "火", "advice": "南方属火，利热情"},
            5: {"direction": "中央", "element": "土", "advice": "中央属土，利稳定"},
            6: {"direction": "中央", "element": "土", "advice": "中央属土，利稳定"},
            7: {"direction": "西方", "element": "金", "advice": "西方属金，利收敛"},
            8: {"direction": "西方", "element": "金", "advice": "西方属金，利收敛"},
            9: {"direction": "北方", "element": "水", "advice": "北方属水，利流动"},
        }
        
        return directions.get(last_digit, {"direction": "中央", "element": "土", "advice": "中性"})
    
    def _generate_metaphysical_advice(self, score: int, compatibility: Dict) -> str:
        """Generate metaphysical advice."""
        if score >= 75:
            return "玄学评分高，可适当关注"
        elif score >= 60:
            return "玄学评分中性，观望为主"
        elif score >= 45:
            return "玄学评分偏低，谨慎操作"
        else:
            return "玄学评分低，建议回避"


def format_metaphysics_analysis(analysis: Dict[str, Any]) -> str:
    """Format metaphysics analysis as readable text."""
    lines = [
        "=" * 50,
        "玄学分析 (仅供参考)",
        "=" * 50,
        f"日期: {analysis.get('date', '')}",
        f"干支: {analysis.get('ganzhi', {}).get('day', '')}",
        f"日主五行: {analysis.get('day_element', '')}",
        f"今日评分: {analysis.get('fortune_score', 0)}/100",
        f"宜: {', '.join(analysis.get('yi', []))}",
        f"忌: {', '.join(analysis.get('ji', []))}",
        "",
        f"有利行业: {', '.join(analysis.get('favorable_sectors', []))}",
        f"不利行业: {', '.join(analysis.get('unfavorable_sectors', []))}",
        "=" * 50,
    ]
    
    return "\n".join(lines)
