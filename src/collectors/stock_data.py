"""Stock data collector module."""

import time
from typing import Dict, List, Any
from datetime import datetime, timedelta

import akshare as ak
import pandas as pd
import requests
from loguru import logger


class StockDataCollector:
    """Collect stock market data from akshare."""
    
    def __init__(self):
        """Initialize stock data collector."""
        self.cache = {}
        self.max_retries = 3
        self.retry_delay = 2
    
    def _retry_request(self, func, *args, **kwargs):
        """Retry a function with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Retry {attempt + 1}/{self.max_retries} after {delay}s: {e}")
                    time.sleep(delay)
                else:
                    raise e
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get market overview for major indices.
        
        Returns:
            Dictionary with index data
        """
        try:
            # Get major indices
            indices = {
                "shanghai": "000001",  # 上证指数
                "shenzhen": "399001",  # 深证成指
                "chinext": "399006",   # 创业板指
            }
            
            result = {}
            for name, code in indices.items():
                try:
                    df = self._retry_request(
                        ak.stock_zh_index_daily,
                        symbol=f"sh{code}" if code.startswith("0") else f"sz{code}"
                    )
                    if not df.empty:
                        latest = df.iloc[-1]
                        prev = df.iloc[-2] if len(df) > 1 else latest
                        change = ((latest['close'] - prev['close']) / prev['close']) * 100
                        result[name] = {
                            "code": code,
                            "price": float(latest['close']),
                            "change": round(change, 2),
                            "volume": int(latest['volume']),
                            "date": str(latest['date'])
                        }
                except Exception as e:
                    logger.warning(f"Failed to get index {name}: {e}")
                    result[name] = {"code": code, "error": str(e)}
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get market overview: {e}")
            return {}
    
    def get_stock_list(self) -> List[Dict[str, Any]]:
        """Get list of all A-shares.
        
        Returns:
            List of stock dictionaries
        """
        try:
            # Get all A-shares with retry
            df = self._retry_request(ak.stock_zh_a_spot_em)
            
            if df.empty:
                return []
            
            stocks = []
            for _, row in df.iterrows():
                stock = {
                    "code": str(row.get("代码", "")),
                    "name": str(row.get("名称", "")),
                    "price": float(row.get("最新价", 0)),
                    "change": float(row.get("涨跌幅", 0)),
                    "volume": float(row.get("成交量", 0)),
                    "amount": float(row.get("成交额", 0)),
                    "pe": float(row.get("市盈率-动态", 0)) if pd.notna(row.get("市盈率-动态")) else None,
                    "pb": float(row.get("市净率", 0)) if pd.notna(row.get("市净率")) else None,
                    "sector": str(row.get("所属行业", "")) if "所属行业" in row.index else "",
                }
                stocks.append(stock)
            
            logger.info(f"Collected {len(stocks)} stocks")
            return stocks
            
        except Exception as e:
            logger.error(f"Failed to get stock list: {e}")
            return []
    
    def get_stock_price(self, code: str, period: str = "daily") -> pd.DataFrame:
        """Get historical price data for a stock.
        
        Args:
            code: Stock code
            period: Data period (daily, weekly, monthly)
            
        Returns:
            DataFrame with price data
        """
        try:
            df = self._retry_request(ak.stock_zh_a_hist, symbol=code, period=period, adjust="qfq")
            return df
        except Exception as e:
            logger.error(f"Failed to get price for {code}: {e}")
            return pd.DataFrame()
    
    def get_financial_data(self, code: str) -> Dict[str, Any]:
        """Get financial data for a stock.
        
        Args:
            code: Stock code
            
        Returns:
            Dictionary with financial data
        """
        try:
            # Get basic financial indicators
            df = self._retry_request(ak.stock_financial_analysis_indicator, symbol=code)
            
            if df.empty:
                return {}
            
            latest = df.iloc[0]
            return {
                "code": code,
                "roe": float(latest.get("净资产收益率(%)", 0)) if pd.notna(latest.get("净资产收益率(%)")) else None,
                "roa": float(latest.get("总资产报酬率(%)", 0)) if pd.notna(latest.get("总资产报酬率(%)")) else None,
                "gross_margin": float(latest.get("销售毛利率(%)", 0)) if pd.notna(latest.get("销售毛利率(%)")) else None,
                "net_margin": float(latest.get("销售净利率(%)", 0)) if pd.notna(latest.get("销售净利率(%)")) else None,
                "debt_ratio": float(latest.get("资产负债率(%)", 0)) if pd.notna(latest.get("资产负债率(%)")) else None,
            }
            
        except Exception as e:
            logger.error(f"Failed to get financial data for {code}: {e}")
            return {}
    
    def get_sector_data(self) -> List[Dict[str, Any]]:
        """Get sector performance data.
        
        Returns:
            List of sector dictionaries
        """
        try:
            df = self._retry_request(ak.stock_board_industry_name_em)
            
            if df.empty:
                return []
            
            sectors = []
            for _, row in df.iterrows():
                sector = {
                    "name": str(row.get("板块名称", "")),
                    "code": str(row.get("板块代码", "")),
                    "change": float(row.get("涨跌幅", 0)),
                    "volume": float(row.get("成交量", 0)),
                    "amount": float(row.get("成交额", 0)),
                }
                sectors.append(sector)
            
            return sectors
            
        except Exception as e:
            logger.error(f"Failed to get sector data: {e}")
            return []
