"""Strategy analyzer module."""

from typing import Dict, List, Any
from datetime import datetime

from loguru import logger
from src.analyzers.value_investing import ValueInvestingAnalyzer, format_value_analysis
from src.analyzers.chokepoint import ChokepointAnalyzer


class StrategyAnalyzer:
    """Analyze market data and generate trading strategy."""
    
    def __init__(self):
        """Initialize strategy analyzer."""
        self.analysis_results = {}
        self.value_analyzer = ValueInvestingAnalyzer()
        self.chokepoint_analyzer = ChokepointAnalyzer()
    
    def analyze(self, market_data: Dict, stock_list: List[Dict], news_data: List[Dict],
                social_data: List[Dict] = None, policy_data: List[Dict] = None,
                research_data: List[Dict] = None) -> Dict[str, Any]:
        """Perform comprehensive analysis.
        
        Args:
            market_data: Market overview data
            stock_list: List of all stocks
            news_data: List of news articles
            social_data: List of social hot topics
            policy_data: List of government policies
            research_data: List of research papers
            
        Returns:
            Analysis results dictionary
        """
        logger.info("Starting comprehensive analysis...")
        
        results = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "market_overview": market_data,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Analyze market sentiment
        market_sentiment = self._analyze_market_sentiment(market_data)
        results["market_sentiment"] = market_sentiment
        
        # Analyze news impact
        news_impact = self._analyze_news_impact(news_data)
        results["news_impact"] = news_impact
        
        # Analyze social heat
        social_impact = self._analyze_social_heat(social_data or [])
        results["social_impact"] = social_impact
        
        # Analyze policy impact
        policy_impact = self._analyze_policy_impact(policy_data or [])
        results["policy_impact"] = policy_impact
        
        # Analyze research impact
        research_impact = self._analyze_research_impact(research_data or [])
        results["research_impact"] = research_impact
        
        # Analyze sectors
        sector_analysis = self._analyze_sectors(stock_list)
        results["sector_analysis"] = sector_analysis
        
        # Chokepoint analysis (Serenity's framework)
        chokepoint_stocks = self.chokepoint_analyzer.get_chokepoint_stocks()
        results["chokepoint_analysis"] = {
            "stocks": chokepoint_stocks,
            "current_phase": self.chokepoint_analyzer.get_current_phase_stocks(),
            "emerging_phase": self.chokepoint_analyzer.get_emerging_phase_stocks(),
        }
        
        # Risk assessment
        risk_level = self._assess_risk(market_data, stock_list)
        results["risk_level"] = risk_level
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            stock_list, news_data, market_sentiment, risk_level,
            social_impact, policy_impact, research_impact
        )
        results["recommendations"] = recommendations
        
        # Portfolio strategy
        portfolio_strategy = self._generate_portfolio_strategy(recommendations)
        results["portfolio_strategy"] = portfolio_strategy
        
        logger.info("Analysis complete")
        return results
    
    def _analyze_market_sentiment(self, market_data: Dict) -> Dict[str, Any]:
        """Analyze overall market sentiment."""
        sentiment = {
            "overall": "neutral",
            "score": 5.0,
            "factors": []
        }
        
        if not market_data:
            return sentiment
        
        # Calculate average change
        changes = []
        for index, data in market_data.items():
            if isinstance(data, dict) and 'change' in data:
                changes.append(data['change'])
        
        if changes:
            avg_change = sum(changes) / len(changes)
            
            if avg_change > 2:
                sentiment["overall"] = "bullish"
                sentiment["score"] = 8.0
                sentiment["factors"].append("市场整体上涨")
            elif avg_change > 0:
                sentiment["overall"] = "slightly_bullish"
                sentiment["score"] = 6.5
                sentiment["factors"].append("市场小幅上涨")
            elif avg_change > -2:
                sentiment["overall"] = "slightly_bearish"
                sentiment["score"] = 4.0
                sentiment["factors"].append("市场小幅下跌")
            else:
                sentiment["overall"] = "bearish"
                sentiment["score"] = 2.0
                sentiment["factors"].append("市场整体下跌")
        
        return sentiment
    
    def _analyze_news_impact(self, news_data: List[Dict]) -> Dict[str, Any]:
        """Analyze impact of news on market."""
        impact = {
            "total_news": len(news_data),
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "top_impact": []
        }
        
        for news in news_data:
            sentiment = news.get('sentiment', 'neutral')
            if sentiment == 'positive':
                impact["positive"] += 1
            elif sentiment == 'negative':
                impact["negative"] += 1
            else:
                impact["neutral"] += 1
        
        # Sort by impact score
        sorted_news = sorted(news_data, key=lambda x: x.get('impact_score', 0), reverse=True)
        impact["top_impact"] = sorted_news[:5]
        
        return impact
    
    def _analyze_social_heat(self, social_data: List[Dict]) -> Dict[str, Any]:
        """Analyze social media hot topics."""
        impact = {
            "total_topics": len(social_data),
            "finance_related": 0,
            "top_topics": []
        }
        
        for topic in social_data:
            if topic.get('sentiment') == 'finance_related':
                impact["finance_related"] += 1
        
        # Sort by heat (convert to number if possible)
        sorted_topics = sorted(social_data, key=lambda x: int(str(x.get('heat', '0')).replace(',', '')) if str(x.get('heat', '0')).isdigit() else 0, reverse=True)
        impact["top_topics"] = sorted_topics[:5]
        
        return impact
    
    def _analyze_policy_impact(self, policy_data: List[Dict]) -> Dict[str, Any]:
        """Analyze government policy impact."""
        impact = {
            "total_policies": len(policy_data),
            "high_impact": 0,
            "sectors_affected": set(),
            "top_policies": []
        }
        
        for policy in policy_data:
            if policy.get('impact_score', 0) >= 7.0:
                impact["high_impact"] += 1
            for sector in policy.get('impact_sectors', []):
                impact["sectors_affected"].add(sector)
        
        # Convert set to list for JSON serialization
        impact["sectors_affected"] = list(impact["sectors_affected"])
        
        # Sort by impact score
        sorted_policies = sorted(policy_data, key=lambda x: x.get('impact_score', 0), reverse=True)
        impact["top_policies"] = sorted_policies[:5]
        
        return impact
    
    def _analyze_research_impact(self, research_data: List[Dict]) -> Dict[str, Any]:
        """Analyze research paper impact."""
        impact = {
            "total_papers": len(research_data),
            "high_impact": 0,
            "fields_covered": set(),
            "top_papers": []
        }
        
        for paper in research_data:
            if paper.get('impact_score', 0) >= 6.0:
                impact["high_impact"] += 1
            for field in paper.get('related_fields', []):
                impact["fields_covered"].add(field)
        
        # Convert set to list for JSON serialization
        impact["fields_covered"] = list(impact["fields_covered"])
        
        # Sort by impact score
        sorted_papers = sorted(research_data, key=lambda x: x.get('impact_score', 0), reverse=True)
        impact["top_papers"] = sorted_papers[:5]
        
        return impact
    
    def _analyze_sectors(self, stock_list: List[Dict]) -> Dict[str, Any]:
        """Analyze sector performance."""
        sectors = {}
        
        for stock in stock_list:
            sector = stock.get('sector', '未知')
            if sector not in sectors:
                sectors[sector] = {
                    'stocks': [],
                    'avg_change': 0,
                    'total_change': 0,
                    'count': 0
                }
            
            sectors[sector]['stocks'].append(stock)
            sectors[sector]['total_change'] += stock.get('change', 0)
            sectors[sector]['count'] += 1
        
        # Calculate averages
        for sector in sectors:
            if sectors[sector]['count'] > 0:
                sectors[sector]['avg_change'] = sectors[sector]['total_change'] / sectors[sector]['count']
        
        # Sort by average change
        sorted_sectors = dict(sorted(sectors.items(), key=lambda x: x[1]['avg_change'], reverse=True))
        
        return {
            "top_sectors": dict(list(sorted_sectors.items())[:5]),
            "bottom_sectors": dict(list(sorted_sectors.items())[-5:])
        }
    
    def _assess_risk(self, market_data: Dict, stock_list: List[Dict]) -> Dict[str, Any]:
        """Assess overall market risk."""
        risk = {
            "level": "medium",
            "score": 5.0,
            "factors": []
        }
        
        # Check market volatility
        if market_data:
            changes = []
            for index, data in market_data.items():
                if isinstance(data, dict) and 'change' in data:
                    changes.append(abs(data['change']))
            
            if changes:
                avg_volatility = sum(changes) / len(changes)
                if avg_volatility > 3:
                    risk["level"] = "high"
                    risk["score"] = 8.0
                    risk["factors"].append("市场波动较大")
                elif avg_volatility > 1.5:
                    risk["level"] = "medium"
                    risk["score"] = 5.0
                else:
                    risk["level"] = "low"
                    risk["score"] = 3.0
                    risk["factors"].append("市场相对稳定")
        
        # Check for extreme moves in individual stocks
        extreme_moves = [s for s in stock_list if abs(s.get('change', 0)) > 5]
        if len(extreme_moves) > 50:
            risk["factors"].append("多只股票出现极端波动")
            risk["score"] = min(risk["score"] + 1, 10)
        
        return risk
    
    def _generate_recommendations(self, stock_list: List[Dict], news_data: List[Dict], 
                                  market_sentiment: Dict, risk_level: Dict,
                                  social_impact: Dict = None, policy_impact: Dict = None,
                                  research_impact: Dict = None) -> List[Dict[str, Any]]:
        """Generate stock recommendations."""
        recommendations = []
        
        # Filter stocks based on criteria
        for stock in stock_list:
            score = self._calculate_stock_score(stock, news_data, market_sentiment, risk_level,
                                               social_impact, policy_impact, research_impact)
            
            if score > 6.0:  # Only recommend stocks with good scores
                recommendation = {
                    "code": stock.get('code', ''),
                    "name": stock.get('name', ''),
                    "price": stock.get('price', 0),
                    "change": stock.get('change', 0),
                    "score": round(score, 2),
                    "action": "buy" if score > 7 else "hold",
                    "reason": self._generate_reason(stock, score, social_impact, policy_impact, research_impact),
                    "risk": "low" if score > 8 else "medium" if score > 6 else "high",
                    "expected_return": f"{max(5, score * 2):.0f}-{max(10, score * 3):.0f}%"
                }
                recommendations.append(recommendation)
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        # Filter for 1000 RMB capital (prefer low-price stocks)
        affordable = [r for r in recommendations if r['price'] < 100]  # Can buy at least 10 shares
        if affordable:
            recommendations = affordable
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _calculate_stock_score(self, stock: Dict, news_data: List[Dict], 
                               market_sentiment: Dict, risk_level: Dict,
                               social_impact: Dict = None, policy_impact: Dict = None,
                               research_impact: Dict = None) -> float:
        """Calculate score for a stock (aggressive style)."""
        score = 5.0  # Base score
        
        # Price factor (aggressive: prefer mid-price stocks with momentum)
        price = stock.get('price', 0)
        if 10 <= price <= 50:
            score += 1.5  # Sweet spot for aggressive plays
        elif 50 < price <= 100:
            score += 1.0
        elif price > 100:
            score += 0.5  # High price stocks can still be good
        
        # Change factor (aggressive: prefer momentum)
        change = stock.get('change', 0)
        if 0 < change <= 3:
            score += 1.0
        elif 3 < change <= 7:
            score += 1.5  # Momentum play
        elif 7 < change <= 10:
            score += 1.0  # Strong momentum but higher risk
        elif change > 10:
            score += 0.5  # Too hot, be careful
        
        # PE ratio factor (aggressive: can tolerate higher PE for growth)
        pe = stock.get('pe')
        if pe and 0 < pe < 50:
            score += 1.0  # Growth stocks acceptable
        elif pe and 50 <= pe < 100:
            score += 0.5  # High growth premium
        elif pe and pe > 100:
            score -= 0.5  # Too expensive
        
        # Volume factor
        volume = stock.get('volume', 0)
        if volume > 1000000:
            score += 0.5
        
        # Market sentiment factor
        sentiment_score = market_sentiment.get('score', 5)
        score += (sentiment_score - 5) * 0.2
        
        # Risk factor
        risk_score = risk_level.get('score', 5)
        score -= (risk_score - 5) * 0.1
        
        # Social heat factor
        if social_impact and social_impact.get('finance_related', 0) > 3:
            score += 0.3
        
        # Policy factor
        if policy_impact and policy_impact.get('high_impact', 0) > 0:
            stock_sector = stock.get('sector', '')
            if stock_sector in policy_impact.get('sectors_affected', []):
                score += 1.0
        
        # Research factor
        if research_impact and research_impact.get('high_impact', 0) > 0:
            stock_sector = stock.get('sector', '')
            if stock_sector in str(research_impact.get('fields_covered', [])):
                score += 0.5
        
        return min(max(score, 0), 10)
    
    def _generate_reason(self, stock: Dict, score: float, social_impact: Dict = None,
                         policy_impact: Dict = None, research_impact: Dict = None) -> str:
        """Generate recommendation reason (aggressive style)."""
        reasons = []
        
        price = stock.get('price', 0)
        if 10 <= price <= 50:
            reasons.append("价格区间适合激进操作")
        
        change = stock.get('change', 0)
        if 3 < change <= 10:
            reasons.append("强势上涨，动量充足")
        
        pe = stock.get('pe')
        if pe and 0 < pe < 50:
            reasons.append("成长性好，估值可接受")
        
        # Check if stock sector is affected by policy
        stock_sector = stock.get('sector', '')
        if policy_impact and stock_sector in policy_impact.get('sectors_affected', []):
            reasons.append("政策风口")
        
        # Check if stock sector is affected by research
        if research_impact and stock_sector in str(research_impact.get('fields_covered', [])):
            reasons.append("科研热点")
        
        if score > 8:
            reasons.append("强势标的")
        elif score > 7:
            reasons.append("优质标的")
        
        return "，".join(reasons) if reasons else "综合表现良好"
    
    def _generate_portfolio_strategy(self, recommendations: List[Dict]) -> Dict[str, Any]:
        """Generate aggressive portfolio strategy for 1000 RMB capital."""
        capital = 1000
        strategy = {
            "capital": capital,
            "broker": "金元证券",
            "style": "激进型",
            "allocated": 0,
            "cash_reserve": 0,  # Aggressive: no cash reserve, all in
            "positions": [],
            "summary": ""
        }
        
        available = capital - strategy["cash_reserve"]
        
        # Aggressive: concentrate on top 2 stocks
        for rec in recommendations[:2]:  # Max 2 positions for concentration
            if available <= 0:
                break
            
            price = rec.get('price', 0)
            if price <= 0:
                continue
            
            # For A-shares, minimum buy is 100 shares (1手)
            # Calculate how many lots we can buy
            lot_price = price * 100  # 1手的价格
            
            if lot_price <= available:
                # Can buy 1 lot
                shares = 100
                cost = lot_price
            else:
                # Can't afford 1 lot, skip
                continue
            
            if cost <= available:
                position = {
                    "code": rec.get('code'),
                    "name": rec.get('name'),
                    "price": price,
                    "shares": shares,
                    "cost": round(cost, 2),
                    "allocation": round(cost / capital * 100, 1),
                    "action": rec.get('action'),
                    "reason": rec.get('reason')
                }
                strategy["positions"].append(position)
                strategy["allocated"] += cost
                available -= cost
        
        strategy["cash_remaining"] = round(capital - strategy["allocated"], 2)
        
        # Generate summary
        if strategy["positions"]:
            pos_summary = ", ".join([f"{p['name']}({p['shares']}股/{p['allocation']}%)" for p in strategy["positions"]])
            strategy["summary"] = f"激进策略: {pos_summary}，剩余{strategy['cash_remaining']}元"
        else:
            strategy["summary"] = "当前无合适标的，建议等待机会"
        
        return strategy
