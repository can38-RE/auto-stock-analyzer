"""News scraper module for financial news."""

import time
import json
from typing import List, Dict, Any
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from loguru import logger


class NewsScraper:
    """Scrape financial news from multiple sources."""
    
    def __init__(self):
        """Initialize news scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
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
    
    def get_market_news(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get market news from multiple sources.
        
        Args:
            limit: Maximum number of news articles
            
        Returns:
            List of news dictionaries
        """
        all_news = []
        
        # Sina Finance
        try:
            sina_news = self._scrape_sina_finance(limit // 3)
            all_news.extend(sina_news)
        except Exception as e:
            logger.warning(f"Failed to scrape Sina Finance: {e}")
        
        # Eastmoney
        try:
            eastmoney_news = self._scrape_eastmoney(limit // 3)
            all_news.extend(eastmoney_news)
        except Exception as e:
            logger.warning(f"Failed to scrape Eastmoney: {e}")
        
        # cls.cn (财联社)
        try:
            cls_news = self._scrape_cls(limit // 3)
            all_news.extend(cls_news)
        except Exception as e:
            logger.warning(f"Failed to scrape cls.cn: {e}")
        
        # If no news collected, try alternative sources
        if not all_news:
            logger.warning("No news from primary sources, trying alternatives...")
            try:
                alt_news = self._scrape_alternative_news(limit)
                all_news.extend(alt_news)
            except Exception as e:
                logger.warning(f"Failed to scrape alternative news: {e}")
        
        logger.info(f"Collected {len(all_news)} news articles")
        return all_news[:limit]
    
    def _scrape_sina_finance(self, limit: int) -> List[Dict[str, Any]]:
        """Scrape news from Sina Finance."""
        url = "https://finance.sina.com.cn/stock/"
        try:
            response = self._retry_request(url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            
            news_list = []
            # Find news items (simplified selector)
            items = soup.find_all('li', class_='news-item')[:limit]
            
            for item in items:
                link = item.find('a')
                if link:
                    news = {
                        "title": link.get_text(strip=True),
                        "url": link.get('href', ''),
                        "source": "新浪财经",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "content": "",
                        "sentiment": "neutral",
                        "impact_score": 5.0
                    }
                    news_list.append(news)
            
            return news_list
            
        except Exception as e:
            logger.error(f"Sina Finance scraping error: {e}")
            return []
    
    def _scrape_eastmoney(self, limit: int) -> List[Dict[str, Any]]:
        """Scrape news from Eastmoney."""
        url = "https://finance.eastmoney.com/a/czqyw.html"
        try:
            response = self._retry_request(url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            
            news_list = []
            items = soup.find_all('div', class_='news_item')[:limit]
            
            for item in items:
                link = item.find('a')
                if link:
                    news = {
                        "title": link.get_text(strip=True),
                        "url": link.get('href', ''),
                        "source": "东方财富",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "content": "",
                        "sentiment": "neutral",
                        "impact_score": 5.0
                    }
                    news_list.append(news)
            
            return news_list
            
        except Exception as e:
            logger.error(f"Eastmoney scraping error: {e}")
            return []
    
    def _scrape_cls(self, limit: int) -> List[Dict[str, Any]]:
        """Scrape news from cls.cn (财联社)."""
        url = "https://www.cls.cn/telegraph"
        try:
            response = self._retry_request(url)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            
            news_list = []
            items = soup.find_all('div', class_='telegraph-content-box')[:limit]
            
            for item in items:
                title = item.find('span', class_='title')
                if title:
                    news = {
                        "title": title.get_text(strip=True),
                        "url": url,
                        "source": "财联社",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "content": "",
                        "sentiment": "neutral",
                        "impact_score": 5.0
                    }
                    news_list.append(news)
            
            return news_list
            
        except Exception as e:
            logger.error(f"cls.cn scraping error: {e}")
            return []
    
    def _scrape_alternative_news(self, limit: int) -> List[Dict[str, Any]]:
        """Scrape news from alternative sources."""
        news_list = []
        
        # Try 163 Finance
        try:
            url = "https://money.163.com/"
            response = self._retry_request(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            
            items = soup.find_all('a', href=True)[:limit]
            for item in items:
                title = item.get_text(strip=True)
                if title and len(title) > 10:
                    news = {
                        "title": title,
                        "url": item.get('href', ''),
                        "source": "网易财经",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "content": "",
                        "sentiment": "neutral",
                        "impact_score": 4.5
                    }
                    news_list.append(news)
        except Exception as e:
            logger.warning(f"163 Finance scraping error: {e}")
        
        # Try ifeng Finance
        try:
            url = "https://finance.ifeng.com/"
            response = self._retry_request(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'lxml')
            
            items = soup.find_all('a', href=True)[:limit]
            for item in items:
                title = item.get_text(strip=True)
                if title and len(title) > 10:
                    news = {
                        "title": title,
                        "url": item.get('href', ''),
                        "source": "凤凰财经",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "content": "",
                        "sentiment": "neutral",
                        "impact_score": 4.5
                    }
                    news_list.append(news)
        except Exception as e:
            logger.warning(f"ifeng Finance scraping error: {e}")
        
        return news_list
    
    def get_company_news(self, code: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get news for a specific company.
        
        Args:
            code: Stock code
            limit: Maximum number of news articles
            
        Returns:
            List of news dictionaries
        """
        try:
            # Use Eastmoney API for company news
            url = f"https://search-api-web.eastmoney.com/search/jsonp?cb=jQuery&param=%7B%22uid%22%3A%22%22%2C%22keyword%22%3A%22{code}%22%2C%22type%22%3A%5B%22cmsArticleWebOld%22%5D%2C%22client%22%3A%22web%22%2C%22clientType%22%3A%22web%22%2C%22clientVersion%22%3A%22curr%22%2C%22param%22%3A%7B%22cmsArticleWebOld%22%3A%7B%22searchScope%22%3A%22default%22%2C%22sort%22%3A%22default%22%2C%22pageIndex%22%3A1%2C%22pageSize%22%3A{limit}%2C%22preTag%22%3A%22%3Cem%3E%22%2C%22postTag%22%3A%22%3C%2Fem%3E%22%7D%7D%7D"
            
            response = self._retry_request(url)
            # Parse JSONP response
            text = response.text
            json_str = text[text.index('(') + 1:text.rindex(')')]
            
            data = json.loads(json_str)
            
            news_list = []
            for item in data.get('result', {}).get('cmsArticleWebOld', []):
                news = {
                    "title": item.get('title', '').replace('<em>', '').replace('</em>', ''),
                    "url": item.get('url', ''),
                    "source": "东方财富",
                    "time": item.get('date', ''),
                    "content": item.get('content', ''),
                    "sentiment": "neutral",
                    "impact_score": 5.0
                }
                news_list.append(news)
            
            return news_list[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get company news for {code}: {e}")
            return []
