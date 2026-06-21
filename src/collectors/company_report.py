"""Company report collector module."""

from typing import List, Dict, Any
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from loguru import logger


class CompanyReportCollector:
    """Collect company financial reports and announcements."""
    
    def __init__(self):
        """Initialize company report collector."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_financial_reports(self, code: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get financial reports for a company.
        
        Args:
            code: Stock code
            limit: Maximum number of reports
            
        Returns:
            List of report dictionaries
        """
        try:
            # Use Eastmoney API for financial reports
            url = f"https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=sh{code if code.startswith('6') else 'sz'}{code}"
            
            # Alternative: Use direct API
            api_url = f"https://datacenter.eastmoney.com/securities/api/data/v1/get?reportName=RPT_F10_FINANCE_MAINFINADATA&columns=ALL&quoteColumns=&filter=(SECURITY_CODE%3D%22{code}%22)&pageNumber=1&pageSize={limit}&sortTypes=-1&sortColumns=REPORT_DATE"
            
            response = self.session.get(api_url, timeout=10)
            data = response.json()
            
            reports = []
            if data.get('result') and data['result'].get('data'):
                for item in data['result']['data']:
                    report = {
                        "company": item.get('SECURITY_NAME_ABBR', ''),
                        "code": code,
                        "report_type": "季度报告" if 'Q' in str(item.get('REPORT_DATE', '')) else "年度报告",
                        "period": str(item.get('REPORT_DATE', ''))[:10],
                        "revenue": item.get('TOTAL_OPERATE_INCOME', 0),
                        "net_profit": item.get('PARENT_NETPROFIT', 0),
                        "growth_rate": item.get('YSTZ', 0),  # 营收同比增长
                        "quality_score": self._calculate_quality_score(item)
                    }
                    reports.append(report)
            
            return reports
            
        except Exception as e:
            logger.error(f"Failed to get financial reports for {code}: {e}")
            return []
    
    def get_announcements(self, code: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get company announcements.
        
        Args:
            code: Stock code
            limit: Maximum number of announcements
            
        Returns:
            List of announcement dictionaries
        """
        try:
            # Use cninfo.com.cn API
            url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
            
            payload = {
                "stock": code,
                "tabName": "fulltext",
                "pageNum": 1,
                "pageSize": limit,
                "column": "szse" if code.startswith(('0', '3')) else "sse",
                "category": "",
                "plate": "",
                "seDate": ""
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0"
            }
            
            response = self.session.post(url, data=payload, headers=headers, timeout=10)
            data = response.json()
            
            announcements = []
            if data.get('announcements'):
                for item in data['announcements']:
                    announcement = {
                        "title": item.get('announcementTitle', ''),
                        "code": code,
                        "time": datetime.fromtimestamp(item.get('announcementTime', 0) / 1000).strftime("%Y-%m-%d") if item.get('announcementTime') else "",
                        "type": item.get('announcementTypeName', ''),
                        "url": f"http://www.cninfo.com.cn/new/disclosure/detail?announcementId={item.get('announcementId', '')}",
                    }
                    announcements.append(announcement)
            
            return announcements
            
        except Exception as e:
            logger.error(f"Failed to get announcements for {code}: {e}")
            return []
    
    def analyze_report_quality(self, report: Dict) -> Dict[str, Any]:
        """Analyze quality of a financial report.
        
        Args:
            report: Report dictionary
            
        Returns:
            Updated report with quality analysis
        """
        quality_score = report.get('quality_score', 5.0)
        
        # Analyze revenue growth
        growth_rate = report.get('growth_rate', 0)
        if growth_rate > 20:
            quality_score += 1.5
        elif growth_rate > 10:
            quality_score += 1.0
        elif growth_rate > 0:
            quality_score += 0.5
        else:
            quality_score -= 1.0
        
        # Analyze profit margin
        revenue = report.get('revenue', 0)
        net_profit = report.get('net_profit', 0)
        
        if revenue > 0:
            profit_margin = (net_profit / revenue) * 100
            if profit_margin > 20:
                quality_score += 1.0
            elif profit_margin > 10:
                quality_score += 0.5
            elif profit_margin < 0:
                quality_score -= 1.5
        
        report['quality_score'] = min(max(quality_score, 0), 10)
        
        # Generate quality description
        if quality_score >= 8:
            report['quality_level'] = 'excellent'
        elif quality_score >= 6:
            report['quality_level'] = 'good'
        elif quality_score >= 4:
            report['quality_level'] = 'average'
        else:
            report['quality_level'] = 'poor'
        
        return report
    
    def _calculate_quality_score(self, data: Dict) -> float:
        """Calculate initial quality score from raw data.
        
        Args:
            data: Raw financial data
            
        Returns:
            Quality score (0-10)
        """
        score = 5.0
        
        # Check for positive metrics
        if data.get('YSTZ', 0) > 0:  # Revenue growth positive
            score += 0.5
        
        if data.get('PARENT_NETPROFIT', 0) > 0:  # Profit positive
            score += 0.5
        
        # Check for consistent growth (would need historical data for proper check)
        # For now, just check current values
        
        return min(max(score, 0), 10)
