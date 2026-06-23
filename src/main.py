"""Main entry point for AutoStockAnalyzer."""

import sys
from pathlib import Path
from datetime import datetime

from loguru import logger

from src.config.settings import get_config
from src.collectors.stock_data import StockDataCollector
from src.collectors.news_scraper import NewsScraper
from src.collectors.social_heat import SocialHeatCollector
from src.collectors.policy_monitor import PolicyMonitor
from src.collectors.research_paper import ResearchPaperCollector
from src.collectors.company_report import CompanyReportCollector
from src.collectors.mainboard_screener import MainboardScreener
from src.analyzers.strategy import StrategyAnalyzer
from src.analyzers.trend import TrendAnalyzer
from src.analyzers.portfolio import PortfolioTracker
from src.analyzers.metaphysics import MetaphysicsAnalyzer
from src.generators.html_report import HTMLReportGenerator
from src.generators.email_sender import send_daily_report


def setup_logging():
    """Setup logging configuration."""
    config = get_config()
    log_config = config.get("logging", {})
    
    logger.remove()
    logger.add(sys.stderr, level=log_config.get("level", "INFO"))
    logger.add(
        log_config.get("file", "./logs/analyzer.log"),
        rotation=log_config.get("max_size", "10MB"),
        retention=log_config.get("backup_count", 5),
        level=log_config.get("level", "INFO")
    )


def get_session_type() -> str:
    """Determine if this is morning or afternoon session."""
    hour = datetime.now().hour
    if hour < 12:
        return "morning"
    else:
        return "afternoon"


def run_daily_analysis():
    """Run daily stock analysis pipeline."""
    session = get_session_type()
    logger.info(f"Starting {session} stock analysis...")
    
    try:
        # Load configuration
        config = get_config()
        logger.info(f"Market: {config.market.get('name', 'A股')}")
        logger.info(f"Capital: {config.capital.get('initial', 1000)} {config.capital.get('currency', 'CNY')}")
        logger.info(f"Session: {session}")
        
        # Step 1: Collect data
        logger.info("Step 1: Collecting data...")
        stock_collector = StockDataCollector()
        news_collector = NewsScraper()
        social_collector = SocialHeatCollector()
        policy_monitor = PolicyMonitor()
        research_collector = ResearchPaperCollector()
        company_collector = CompanyReportCollector()
        
        market_data = stock_collector.get_market_overview()
        stock_list = stock_collector.get_stock_list()
        news_data = news_collector.get_market_news()
        social_data = social_collector.get_all_hot_topics()
        policy_data = policy_monitor.get_all_policies()
        research_data = research_collector.get_arxiv_papers()
        
        logger.info(f"Collected {len(stock_list)} stocks, {len(news_data)} news, {len(social_data)} social topics")
        logger.info(f"Collected {len(policy_data)} policies, {len(research_data)} research papers")
        
        # Step 1.5: Screen mainboard stocks for aggressive strategy
        logger.info("Step 1.5: Screening mainboard stocks...")
        screener = MainboardScreener()
        budget = config.capital.get('initial', 1900)
        screened_stocks = screener.screen_stocks(budget=budget, top_n=20)
        buy_plan = screener.generate_buy_plan(screened_stocks, budget=budget)
        logger.info(f"Screened {len(screened_stocks)} mainboard stocks, buy plan: {buy_plan['summary']}")
        
        # Step 1.6: Trend analysis for top stocks
        logger.info("Step 1.6: Analyzing trends for top stocks...")
        trend_analyzer = TrendAnalyzer()
        trend_results = trend_analyzer.analyze_multiple(screened_stocks[:10])
        logger.info(f"Completed trend analysis for {len(trend_results)} stocks")
        
        # Step 1.7: Portfolio tracking
        logger.info("Step 1.7: Updating portfolio...")
        portfolio = PortfolioTracker()
        current_prices = {s['code']: s['price'] for s in screened_stocks}
        # Add current holdings prices
        for h in portfolio.get_holdings():
            if h['code'] not in current_prices:
                # Try to get current price
                for s in stock_list:
                    if s.get('code') == h['code']:
                        current_prices[h['code']] = s.get('price', h['price'])
                        break
        
        portfolio_summary = portfolio.get_portfolio_summary(current_prices)
        logger.info(f"Portfolio: {portfolio_summary['holdings_count']} holdings, P&L: {portfolio_summary['total_pnl']:+.2f}元")
        
        # Step 1.8: Metaphysics analysis (玄学分析)
        logger.info("Step 1.8: Running metaphysics analysis...")
        metaphysics = MetaphysicsAnalyzer()
        day_fortune = metaphysics.analyze_day_fortune()
        
        # Analyze top stocks with metaphysics
        metaphysics_results = []
        for stock in screened_stocks[:5]:
            meta = metaphysics.analyze_stock_metaphysics(
                stock['code'], 
                stock.get('name', ''),
                stock.get('sector', '')
            )
            metaphysics_results.append(meta)
        
        logger.info(f"Metaphysics analysis: Day score {day_fortune['fortune_score']}, {len(metaphysics_results)} stocks analyzed")
        
        # Step 2: Analyze data
        logger.info("Step 2: Analyzing data...")
        strategy_analyzer = StrategyAnalyzer()
        analysis_results = strategy_analyzer.analyze(
            market_data=market_data,
            stock_list=stock_list,
            news_data=news_data,
            social_data=social_data,
            policy_data=policy_data,
            research_data=research_data
        )
        
        logger.info(f"Analysis complete. Generated {len(analysis_results.get('recommendations', []))} recommendations")
        
        # Add session info, screener results, portfolio, and metaphysics to analysis
        analysis_results['session'] = session
        analysis_results['session_label'] = "早盘" if session == "morning" else "午盘"
        analysis_results['mainboard_stocks'] = screened_stocks
        analysis_results['buy_plan'] = buy_plan
        analysis_results['trend_analysis'] = trend_results
        analysis_results['portfolio'] = portfolio_summary
        analysis_results['metaphysics'] = day_fortune
        analysis_results['metaphysics_stocks'] = metaphysics_results
        
        # Step 3: Generate report
        logger.info("Step 3: Generating report...")
        report_generator = HTMLReportGenerator()
        report_path = report_generator.generate(analysis_results)
        
        logger.info(f"Report generated: {report_path}")
        
        # Step 4: Send email
        logger.info("Step 4: Sending email...")
        email_sent = send_daily_report(report_path)
        if email_sent:
            logger.info("Email sent successfully!")
        else:
            logger.warning("Email sending skipped or failed")
        
        logger.info("Daily analysis completed successfully!")
        
        return report_path
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise


def main():
    """Main entry point."""
    setup_logging()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode
        logger.info("Running in test mode...")
        config = get_config()
        logger.info(f"Config loaded: {config.market.get('name')}")
        return
    
    run_daily_analysis()


if __name__ == "__main__":
    main()
