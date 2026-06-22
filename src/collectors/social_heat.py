"""Social heat collector module."""

import time
from typing import List, Dict, Any
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from loguru import logger


class SocialHeatCollector:
    """Collect social media hot topics."""
    
    def __init__(self):
        """Initialize social heat collector."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        self.max_retries = 3
        self.retry_delay = 2
    
    def _retry_request(self, url, timeout=15, **kwargs):
        """Retry a request with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=timeout, **kwargs)
                response.raise_for_status()
                return response
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {url}: {e}")
                    time.sleep(delay)
                else:
                    raise e
    
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
            
            response = self._retry_request(url)
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
            
            response = self._retry_request(url)
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
            
            response = self._retry_request(url)
            response.encoding = 'utf-8'
            
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
    
    def get_all_hot_topics(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get hot topics from all platforms.
        
        Args:
            limit: Maximum number of topics per platform
            
        Returns:
            List of hot topic dictionaries
        """
        all_topics = []
        
        # Weibo
        try:
            weibo_topics = self.get_weibo_hot(limit)
            all_topics.extend(weibo_topics)
        except Exception as e:
            logger.warning(f"Failed to get Weibo topics: {e}")
        
        # Zhihu
        try:
            zhihu_topics = self.get_zhihu_hot(limit)
            all_topics.extend(zhihu_topics)
        except Exception as e:
            logger.warning(f"Failed to get Zhihu topics: {e}")
        
        # Baidu
        try:
            baidu_topics = self.get_baidu_hot(limit)
            all_topics.extend(baidu_topics)
        except Exception as e:
            logger.warning(f"Failed to get Baidu topics: {e}")
        
        logger.info(f"Collected {len(all_topics)} hot topics from all platforms")
        return all_topics
    
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
            "经济", "金融", "投资", "理财", "银行", "保险",
        ]
        
        filtered = []
        for topic in topics:
            title = topic.get('topic', '')
            if any(keyword in title for keyword in finance_keywords):
                topic['sentiment'] = 'finance_related'
                filtered.append(topic)
        
        return filtered
