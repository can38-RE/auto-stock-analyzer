"""Social heat collector module."""

from typing import List, Dict, Any
from datetime import datetime

import requests
from loguru import logger


class SocialHeatCollector:
    """Collect social media hot topics."""
    
    def __init__(self):
        """Initialize social heat collector."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_weibo_hot(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get Weibo hot topics.
        
        Args:
            limit: Maximum number of topics
            
        Returns:
            List of hot topic dictionaries
        """
        try:
            # Use Weibo mobile API
            url = "https://m.weibo.cn/api/container/getIndex?containerid=106003type%3D25%26t%3D3%26disable_hot%3D1%26filter_type%3Drealtimehot"
            
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            topics = []
            cards = data.get('data', {}).get('cards', [])
            
            for card in cards:
                if card.get('card_type') == 9:
                    card_group = card.get('card_group', [])
                    for item in card_group:
                        if item.get('card_type') == 11:
                            desc = item.get('desc', '')
                            if desc:
                                topic = {
                                    "topic": desc,
                                    "heat": item.get('desc_extr', '0'),
                                    "platform": "weibo",
                                    "related_stocks": [],
                                    "sentiment": "neutral"
                                }
                                topics.append(topic)
            
            return topics[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get Weibo hot topics: {e}")
            return []
    
    def get_zhihu_hot(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get Zhihu hot topics.
        
        Args:
            limit: Maximum number of topics
            
        Returns:
            List of hot topic dictionaries
        """
        try:
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"
            
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            topics = []
            for item in data.get('data', []):
                target = item.get('target', {})
                title = target.get('title', '')
                if title:
                    topic = {
                        "topic": title,
                        "heat": item.get('detail_text', '0'),
                        "platform": "zhihu",
                        "related_stocks": [],
                        "sentiment": "neutral"
                    }
                    topics.append(topic)
            
            return topics[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get Zhihu hot topics: {e}")
            return []
    
    def get_baidu_hot(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get Baidu hot topics.
        
        Args:
            limit: Maximum number of topics
            
        Returns:
            List of hot topic dictionaries
        """
        try:
            url = "https://top.baidu.com/board?tab=realtime"
            
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            
            topics = []
            items = soup.find_all('div', class_='category-wrap_iQLoo')[:limit]
            
            for item in items:
                title = item.find('div', class_='c-single-text-ellipsis')
                if title:
                    topic = {
                        "topic": title.get_text(strip=True),
                        "heat": "0",
                        "platform": "baidu",
                        "related_stocks": [],
                        "sentiment": "neutral"
                    }
                    topics.append(topic)
            
            return topics[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get Baidu hot topics: {e}")
            return []
    
    def filter_finance_related(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter finance-related topics.
        
        Args:
            topics: List of all topics
            
        Returns:
            Filtered list of finance-related topics
        """
        finance_keywords = [
            "股票", "基金", "股市", "A股", "涨停", "跌停", "牛市", "熊市",
            "央行", "降息", "降准", "利率", "GDP", "CPI", "PPI",
            "新能源", "半导体", "芯片", "人工智能", "AI",
            "茅台", "比亚迪", "宁德时代", "腾讯", "阿里巴巴",
        ]
        
        filtered = []
        for topic in topics:
            title = topic.get('topic', '')
            if any(keyword in title for keyword in finance_keywords):
                topic['sentiment'] = 'finance_related'
                filtered.append(topic)
        
        return filtered
