"""Sector Rotation Detection Module.

Detects hot sectors and capital flow patterns to identify rotation opportunities.
"""

import baostock as bs
from datetime import datetime, timedelta
from typing import List, Dict, Any
from loguru import logger


class SectorRotationDetector:
    """Detect sector rotation patterns in A-share market."""
    
    def __init__(self):
        self._logged_in = False
    
    def _login(self):
        if not self._logged_in:
            bs.login()
            self._logged_in = True
    
    def _logout(self):
        if self._logged_in:
            bs.logout()
            self._logged_in = False
    
    def get_sector_performance(self, days: int = 5) -> List[Dict[str, Any]]:
        """Get sector performance data.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            List of sectors with performance metrics
        """
        self._login()
        
        today = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days + 5)).strftime("%Y-%m-%d")
        
        # A-share sector codes (mainboard sectors)
        sector_codes = [
            "sh.000001",  # 上证指数
            "sz.399001",  # 深证成指
            "sz.399006",  # 创业板指
            "sh.000016",  # 上证50
            "sh.000300",  # 沪深300
            "sh.000905",  # 中证500
        ]
        
        sectors = []
        
        for code in sector_codes:
            try:
                rs = bs.query_history_k_data_plus(
                    code,
                    "date,close,volume",
                    start_date=start_date,
                    end_date=today,
                    frequency='d',
                    adjustflag='3'
                )
                
                data = []
                while (rs.error_code == '0') and rs.next():
                    data.append(rs.get_row_data())
                
                if len(data) < 3:
                    continue
                
                closes = [float(d[1]) for d in data if d[1]]
                volumes = [float(d[2]) for d in data if d[2]]
                
                if len(closes) < 3:
                    continue
                
                # Calculate performance
                change_1d = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) >= 2 else 0
                change_3d = ((closes[-1] - closes[-4]) / closes[-4] * 100) if len(closes) >= 4 else 0
                change_5d = ((closes[-1] - closes[-6]) / closes[-6] * 100) if len(closes) >= 6 else 0
                
                # Volume trend
                avg_vol_recent = sum(volumes[-3:]) / 3 if len(volumes) >= 3 else 0
                avg_vol_earlier = sum(volumes[-6:-3]) / 3 if len(volumes) >= 6 else 0
                vol_change = ((avg_vol_recent - avg_vol_earlier) / avg_vol_earlier * 100) if avg_vol_earlier > 0 else 0
                
                # Get sector name
                rs2 = bs.query_stock_basic(code=code)
                name = ""
                while (rs2.error_code == '0') and rs2.next():
                    name = rs2.get_row_data()[1]
                
                sectors.append({
                    'code': code.split('.')[1],
                    'name': name,
                    'price': closes[-1],
                    'change_1d': round(change_1d, 2),
                    'change_3d': round(change_3d, 2),
                    'change_5d': round(change_5d, 2),
                    'vol_change': round(vol_change, 2),
                    'momentum': round((change_3d * 0.4 + change_5d * 0.6), 2),  # Weighted momentum
                })
                
            except Exception as e:
                logger.warning(f"Failed to get sector {code}: {e}")
                continue
        
        self._logout()
        
        # Sort by momentum
        sectors.sort(key=lambda x: -x['momentum'])
        
        return sectors
    
    def detect_rotation(self, sectors: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect sector rotation patterns.
        
        Args:
            sectors: List of sector performance data
            
        Returns:
            Rotation analysis results
        """
        if not sectors:
            return {'rotation_detected': False, 'message': 'No data available'}
        
        # Identify hot sectors (high momentum + volume increase)
        hot_sectors = [s for s in sectors if s['momentum'] > 5 and s['vol_change'] > 10]
        
        # Identify cooling sectors (negative momentum)
        cooling_sectors = [s for s in sectors if s['momentum'] < -2]
        
        # Detect rotation pattern
        rotation_detected = len(hot_sectors) > 0 and len(cooling_sectors) > 0
        
        # Generate recommendations
        recommendations = []
        if hot_sectors:
            recommendations.append(f"关注热点板块: {', '.join([s['name'] for s in hot_sectors[:3]])}")
        if cooling_sectors:
            recommendations.append(f"回避冷却板块: {', '.join([s['name'] for s in cooling_sectors[:3]])}")
        
        return {
            'rotation_detected': rotation_detected,
            'hot_sectors': hot_sectors,
            'cooling_sectors': cooling_sectors,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }


def format_rotation_report(sectors: List[Dict[str, Any]], rotation: Dict[str, Any]) -> str:
    """Format rotation analysis as readable text."""
    lines = [
        "=" * 60,
        "板块轮动分析",
        "=" * 60,
        "",
        "板块表现排名:",
        f"{'排名':<4} {'板块':<15} {'今日':>8} {'3日':>8} {'5日':>8} {'动量':>8}",
        "-" * 60,
    ]
    
    for i, s in enumerate(sectors[:10], 1):
        lines.append(f"{i:<4} {s['name']:<15} {s['change_1d']:>+7.2f}% {s['change_3d']:>+7.2f}% {s['change_5d']:>+7.2f}% {s['momentum']:>+7.2f}")
    
    lines.extend([
        "",
        "轮动分析:",
        f"  检测到轮动: {'是' if rotation.get('rotation_detected') else '否'}",
    ])
    
    if rotation.get('hot_sectors'):
        lines.append(f"  热点板块: {', '.join([s['name'] for s in rotation['hot_sectors']])}")
    
    if rotation.get('cooling_sectors'):
        lines.append(f"  冷却板块: {', '.join([s['name'] for s in rotation['cooling_sectors']])}")
    
    if rotation.get('recommendations'):
        lines.append("\n建议:")
        for rec in rotation['recommendations']:
            lines.append(f"  • {rec}")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
