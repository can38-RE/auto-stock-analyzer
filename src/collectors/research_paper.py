"""Research paper collector module."""

from typing import List, Dict, Any
from datetime import datetime, timedelta

import requests
from loguru import logger


class ResearchPaperCollector:
    """Collect research papers and tech news."""
    
    def __init__(self):
        """Initialize research paper collector."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def get_arxiv_papers(self, category: str = "cs.AI", limit: int = 20) -> List[Dict[str, Any]]:
        """Get papers from arXiv.
        
        Args:
            category: arXiv category (e.g., cs.AI, cs.LG, physics)
            limit: Maximum number of papers
            
        Returns:
            List of paper dictionaries
        """
        try:
            url = f"http://export.arxiv.org/api/query?search_query=cat:{category}&start=0&max_results={limit}&sortBy=submittedDate&sortOrder=descending"
            
            response = self.session.get(url, timeout=15)
            
            # Parse XML response
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            
            papers = []
            entries = soup.find_all('entry')
            
            for entry in entries:
                title = entry.find('title').get_text(strip=True) if entry.find('title') else ""
                abstract = entry.find('summary').get_text(strip=True) if entry.find('summary') else ""
                published = entry.find('published').get_text(strip=True) if entry.find('published') else ""
                
                paper = {
                    "title": title,
                    "abstract": abstract[:500],  # Truncate long abstracts
                    "source": "arXiv",
                    "category": category,
                    "published": published,
                    "related_fields": [],
                    "related_stocks": [],
                    "impact_score": 5.0
                }
                
                # Map papers to potential stock sectors
                paper = self._map_paper_to_sectors(paper)
                papers.append(paper)
            
            return papers
            
        except Exception as e:
            logger.error(f"Failed to get arXiv papers: {e}")
            return []
    
    def get_tech_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get tech news from various sources.
        
        Args:
            limit: Maximum number of news
            
        Returns:
            List of tech news dictionaries
        """
        news_list = []
        
        # 36kr
        try:
            kr_news = self._scrape_36kr(limit // 3)
            news_list.extend(kr_news)
        except Exception as e:
            logger.warning(f"Failed to scrape 36kr: {e}")
        
        # TechCrunch (Chinese)
        try:
            tc_news = self._scrape_techcrunch(limit // 3)
            news_list.extend(tc_news)
        except Exception as e:
            logger.warning(f"Failed to scrape TechCrunch: {e}")
        
        # IT之家
        try:
            ithome_news = self._scrape_ithome(limit // 3)
            news_list.extend(ithome_news)
        except Exception as e:
            logger.warning(f"Failed to scrape IT之家: {e}")
        
        return news_list[:limit]
    
    def _scrape_36kr(self, limit: int) -> List[Dict[str, Any]]:
        """Scrape news from 36kr."""
        url = "https://36kr.com/newsflashes"
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            
            news_list = []
            items = soup.find_all('a', class_='article-item-title')[:limit]
            
            for item in items:
                news = {
                    "title": item.get_text(strip=True),
                    "url": item.get('href', ''),
                    "source": "36氪",
                    "time": datetime.now().strftime("%Y-%m-%d"),
                    "content": "",
                    "related_fields": ["科技", "创业"],
                    "related_stocks": [],
                    "impact_score": 5.0
                }
                news_list.append(news)
            
            return news_list
            
        except Exception as e:
            logger.error(f"36kr scraping error: {e}")
            return []
    
    def _scrape_techcrunch(self, limit: int) -> List[Dict[str, Any]]:
        """Scrape news from TechCrunch China."""
        # Use RSS feed
        url = "https://techcrunch.cn/feed/"
        try:
            response = self.session.get(url, timeout=10)
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            
            news_list = []
            items = soup.find_all('item')[:limit]
            
            for item in items:
                title = item.find('title').get_text(strip=True) if item.find('title') else ""
                news = {
                    "title": title,
                    "url": "",
                    "source": "TechCrunch",
                    "time": datetime.now().strftime("%Y-%m-%d"),
                    "content": "",
                    "related_fields": ["科技", "互联网"],
                    "related_stocks": [],
                    "impact_score": 5.0
                }
                news_list.append(news)
            
            return news_list
            
        except Exception as e:
            logger.error(f"TechCrunch scraping error: {e}")
            return []
    
    def _scrape_ithome(self, limit: int) -> List[Dict[str, Any]]:
        """Scrape news from IT之家."""
        url = "https://www.ithome.com/"
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')
            
            news_list = []
            items = soup.find_all('a', class_='title')[:limit]
            
            for item in items:
                news = {
                    "title": item.get_text(strip=True),
                    "url": item.get('href', ''),
                    "source": "IT之家",
                    "time": datetime.now().strftime("%Y-%m-%d"),
                    "content": "",
                    "related_fields": ["科技", "数码"],
                    "related_stocks": [],
                    "impact_score": 4.5
                }
                news_list.append(news)
            
            return news_list
            
        except Exception as e:
            logger.error(f"IT之家 scraping error: {e}")
            return []
    
    def _map_paper_to_sectors(self, paper: Dict) -> Dict:
        """Map paper to potential stock sectors.
        
        Args:
            paper: Paper dictionary
            
        Returns:
            Updated paper with sector mappings
        """
        title = paper.get('title', '').lower()
        abstract = paper.get('abstract', '').lower()
        
        sector_mapping = {
            "人工智能": ["ai", "artificial intelligence", "machine learning", "deep learning", "neural network"],
            "新能源": ["solar", "battery", "energy", "photovoltaic", "wind"],
            "半导体": ["chip", "semiconductor", "processor", "gpu", "tpu"],
            "生物医药": ["drug", "pharmaceutical", "medical", "healthcare", "biotech"],
            "量子计算": ["quantum", "qubit"],
            "自动驾驶": ["autonomous", "self-driving", "vehicle"],
            "机器人": ["robot", "robotics"],
        }
        
        related_fields = []
        for field, keywords in sector_mapping.items():
            if any(keyword in title or keyword in abstract for keyword in keywords):
                related_fields.append(field)
        
        paper['related_fields'] = related_fields
        
        # Calculate impact score based on relevance
        if len(related_fields) > 2:
            paper['impact_score'] = 7.0
        elif len(related_fields) > 0:
            paper['impact_score'] = 6.0
        
        return paper
