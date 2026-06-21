"""Policy monitor module for tracking government policies."""

from typing import List, Dict, Any
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from loguru import logger


class PolicyMonitor:
    """Monitor government policies and regulations."""
    
    def __init__(self):
        """Initialize policy monitor."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_state_council_policies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get policies from State Council.
        
        Args:
            limit: Maximum number of policies
            
        Returns:
            List of policy dictionaries
        """
        try:
            url = "http://www.gov.cn/zhengce/zuixin/"
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            
            policies = []
            items = soup.find_all('li', class_='li')[:limit]
            
            for item in items:
                link = item.find('a')
                if link:
                    policy = {
                        "title": link.get_text(strip=True),
                        "url": link.get('href', ''),
                        "source": "国务院",
                        "time": datetime.now().strftime("%Y-%m-%d"),
                        "content": "",
                        "impact_sectors": [],
                        "impact_stocks": [],
                        "impact_score": 5.0
                    }
                    policies.append(policy)
            
            return policies
            
        except Exception as e:
            logger.error(f"Failed to get State Council policies: {e}")
            return []
    
    def get_central_bank_policies(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get policies from People's Bank of China.
        
        Args:
            limit: Maximum number of policies
            
        Returns:
            List of policy dictionaries
        """
        try:
            url = "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html"
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            
            policies = []
            items = soup.find_all('li')[:limit]
            
            for item in items:
                link = item.find('a')
                if link:
                    policy = {
                        "title": link.get_text(strip=True),
                        "url": link.get('href', ''),
                        "source": "央行",
                        "time": datetime.now().strftime("%Y-%m-%d"),
                        "content": "",
                        "impact_sectors": ["金融", "银行"],
                        "impact_stocks": [],
                        "impact_score": 6.0
                    }
                    policies.append(policy)
            
            return policies
            
        except Exception as e:
            logger.error(f"Failed to get Central Bank policies: {e}")
            return []
    
    def get_regulatory_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news from CSRC (证监会).
        
        Args:
            limit: Maximum number of news
            
        Returns:
            List of news dictionaries
        """
        try:
            url = "http://www.csrc.gov.cn/csrc/c100028/common_list.shtml"
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            
            news_list = []
            items = soup.find_all('li')[:limit]
            
            for item in items:
                link = item.find('a')
                if link:
                    news = {
                        "title": link.get_text(strip=True),
                        "url": link.get('href', ''),
                        "source": "证监会",
                        "time": datetime.now().strftime("%Y-%m-%d"),
                        "content": "",
                        "impact_sectors": ["证券", "基金"],
                        "impact_stocks": [],
                        "impact_score": 5.5
                    }
                    news_list.append(news)
            
            return news_list
            
        except Exception as e:
            logger.error(f"Failed to get regulatory news: {e}")
            return []
    
    def analyze_policy_impact(self, policy: Dict) -> Dict[str, Any]:
        """Analyze impact of a policy.
        
        Args:
            policy: Policy dictionary
            
        Returns:
            Analysis results
        """
        title = policy.get('title', '').lower()
        
        # Simple keyword-based impact analysis
        sector_keywords = {
            "新能源": ["新能源", "光伏", "风电", "储能", "电动车"],
            "半导体": ["芯片", "半导体", "集成电路"],
            "医药": ["医药", "医疗", "药品", "医保"],
            "房地产": ["房地产", "楼市", "住房"],
            "金融": ["银行", "保险", "证券", "基金"],
            "科技": ["科技", "人工智能", "AI", "互联网"],
        }
        
        impact_sectors = []
        for sector, keywords in sector_keywords.items():
            if any(keyword in title for keyword in keywords):
                impact_sectors.append(sector)
        
        policy['impact_sectors'] = impact_sectors
        
        # Calculate impact score based on source
        source_scores = {
            "国务院": 9.0,
            "央行": 8.5,
            "证监会": 7.5,
            "发改委": 7.0,
        }
        
        policy['impact_score'] = source_scores.get(policy.get('source', ''), 5.0)
        
        return policy
