"""Main entry point for AutoStockAnalyzer."""

import sys
from pathlib import Path

from loguru import logger

from src.config.settings import get_config
from src.collectors.stock_data import StockDataCollector
from src.collectors.news_scraper import NewsScraper
from src.analyzers.strategy import StrategyAnalyzer
from src.generators.html_report import HTMLReportGenerator


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


def run_daily_analysis():
    """Run daily stock analysis pipeline."""
    logger.info("Starting daily stock analysis...")
    
    try:
        # Load configuration
        config = get_config()
        logger.info(f"Market: {config.market.get('name', 'A股')}")
        logger.info(f"Capital: {config.capital.get('initial', 1000)} {config.capital.get('currency', 'CNY')}")
        
        # Step 1: Collect data
        logger.info("Step 1: Collecting data...")
        stock_collector = StockDataCollector()
        news_collector = NewsScraper()
        
        market_data = stock_collector.get_market_overview()
        stock_list = stock_collector.get_stock_list()
        news_data = news_collector.get_market_news()
        
        logger.info(f"Collected {len(stock_list)} stocks, {len(news_data)} news articles")
        
        # Step 2: Analyze data
        logger.info("Step 2: Analyzing data...")
        strategy_analyzer = StrategyAnalyzer()
        analysis_results = strategy_analyzer.analyze(
            market_data=market_data,
            stock_list=stock_list,
            news_data=news_data
        )
        
        logger.info(f"Analysis complete. Generated {len(analysis_results.get('recommendations', []))} recommendations")
        
        # Step 3: Generate report
        logger.info("Step 3: Generating report...")
        report_generator = HTMLReportGenerator()
        report_path = report_generator.generate(analysis_results)
        
        logger.info(f"Report generated: {report_path}")
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
