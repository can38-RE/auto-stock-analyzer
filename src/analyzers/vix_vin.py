"""VIX/VIN Dual Monitoring Module.

Monitors both US VIX and China iVIX (VIN) for market volatility assessment.
"""

import requests
import baostock as bs
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from loguru import logger


class VIXVINMonitor:
    """Monitor VIX (US) and iVIX (China) volatility indices."""
    
    def __init__(self):
        self._logged_in = False
    
    def _login_baostock(self):
        if not self._logged_in:
            bs.login()
            self._logged_in = True
    
    def _logout_baostock(self):
        if self._logged_in:
            bs.logout()
            self._logged_in = False
    
    def get_vix(self) -> Dict[str, Any]:
        """Get VIX data from Yahoo Finance."""
        try:
            # Use Yahoo Finance API
            url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EVIX?range=5d&interval=1d"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            if 'chart' in data and 'result' in data['chart']:
                result = data['chart']['result'][0]
                meta = result['meta']
                price = meta.get('regularMarketPrice', 0)
                prev_close = meta.get('chartPreviousClose', 0)
                
                return {
                    'name': 'VIX',
                    'price': price,
                    'prev_close': prev_close,
                    'change': ((price - prev_close) / prev_close * 100) if prev_close > 0 else 0,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'Yahoo Finance'
                }
            
            return {'name': 'VIX', 'price': 0, 'error': 'No data'}
            
        except Exception as e:
            logger.error(f"Failed to get VIX: {e}")
            return {'name': 'VIX', 'price': 0, 'error': str(e)}
    
    def get_ivix(self) -> Dict[str, Any]:
        """Get iVIX (China VIX) from baostock."""
        try:
            self._login_baostock()
            
            today = datetime.now().strftime("%Y-%m-%d")
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            
            # iVIX index code
            rs = bs.query_history_k_data_plus(
                "sh.000188",
                "date,close",
                start_date=week_ago,
                end_date=today,
                frequency='d'
            )
            
            data = []
            while (rs.error_code == '0') and rs.next():
                data.append(rs.get_row_data())
            
            if data:
                latest = data[-1]
                price = float(latest[1]) if latest[1] else 0
                
                # Calculate change
                prev_price = float(data[-2][1]) if len(data) >= 2 and data[-2][1] else price
                change = ((price - prev_price) / prev_price * 100) if prev_price > 0 else 0
                
                return {
                    'name': 'iVIX',
                    'price': price,
                    'prev_close': prev_price,
                    'change': change,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'baostock'
                }
            
            return {'name': 'iVIX', 'price': 0, 'error': 'No data'}
            
        except Exception as e:
            logger.error(f"Failed to get iVIX: {e}")
            return {'name': 'iVIX', 'price': 0, 'error': str(e)}
    
    def get_vix_vin_assessment(self) -> Dict[str, Any]:
        """Get combined VIX/VIN assessment."""
        vix = self.get_vix()
        ivix = self.get_ivix()
        
        # Score based on VIX
        vix_price = vix.get('price', 0)
        if vix_price < 15:
            vix_score = 80
            vix_status = "低波动"
            vix_advice = "积极买入"
        elif vix_price < 25:
            vix_score = 60
            vix_status = "正常波动"
            vix_advice = "正常操作"
        elif vix_price < 30:
            vix_score = 40
            vix_status = "高波动"
            vix_advice = "谨慎操作"
        else:
            vix_score = 20
            vix_status = "极高波动"
            vix_advice = "防御模式"
        
        # Score based on iVIX
        ivix_price = ivix.get('price', 0)
        if ivix_price < 15:
            ivix_score = 80
            ivix_status = "低波动"
            ivix_advice = "积极买入"
        elif ivix_price < 25:
            ivix_score = 60
            ivix_status = "正常波动"
            ivix_advice = "正常操作"
        elif ivix_price < 30:
            ivix_score = 40
            ivix_status = "高波动"
            ivix_advice = "谨慎操作"
        else:
            ivix_score = 20
            ivix_status = "极高波动"
            ivix_advice = "防御模式"
        
        # Combined score
        combined_score = (vix_score + ivix_score) / 2
        
        # Generate recommendations
        recommendations = []
        if vix_price > 25:
            recommendations.append("美国市场波动较大，注意风险")
        if ivix_price > 25:
            recommendations.append("A股市场波动较大，谨慎操作")
        if vix_price < 15 and ivix_price < 15:
            recommendations.append("全球市场平稳，可积极操作")
        
        return {
            'vix': vix,
            'ivix': ivix,
            'vix_score': vix_score,
            'vix_status': vix_status,
            'vix_advice': vix_advice,
            'ivix_score': ivix_score,
            'ivix_status': ivix_status,
            'ivix_advice': ivix_advice,
            'combined_score': combined_score,
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }


def format_vix_vin_report(assessment: Dict[str, Any]) -> str:
    """Format VIX/VIN assessment as readable text."""
    lines = [
        "=" * 60,
        "VIX/VIN 双重波动率监测",
        "=" * 60,
        "",
        "VIX (美国恐慌指数):",
        f"  当前值: {assessment['vix'].get('price', 0):.2f}",
        f"  状态: {assessment['vix_status']}",
        f"  建议: {assessment['vix_advice']}",
        "",
        "iVIX (中国波指):",
        f"  当前值: {assessment['ivix'].get('price', 0):.2f}",
        f"  状态: {assessment['ivix_status']}",
        f"  建议: {assessment['ivix_advice']}",
        "",
        f"综合评分: {assessment['combined_score']:.0f}/100",
        "",
        "建议:",
    ]
    
    for rec in assessment['recommendations']:
        lines.append(f"  • {rec}")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
