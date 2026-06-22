"""Stock data collector module."""

import time
from typing import Dict, List, Any
from datetime import datetime, timedelta

import pandas as pd
from loguru import logger


class StockDataCollector:
    """Collect stock market data from multiple sources."""
    
    def __init__(self):
        """Initialize stock data collector."""
        self.cache = {}
        self.max_retries = 3
        self.retry_delay = 2
        self._baostock_logged_in = False
    
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
    
    def _login_baostock(self):
        """Login to baostock."""
        if not self._baostock_logged_in:
            try:
                import baostock as bs
                lg = bs.login()
                if lg.error_code == '0':
                    self._baostock_logged_in = True
                    logger.info("BaoStock login successful")
                else:
                    logger.error(f"BaoStock login failed: {lg.error_msg}")
            except Exception as e:
                logger.error(f"BaoStock login error: {e}")
    
    def _logout_baostock(self):
        """Logout from baostock."""
        if self._baostock_logged_in:
            try:
                import baostock as bs
                bs.logout()
                self._baostock_logged_in = False
            except Exception as e:
                logger.warning(f"BaoStock logout error: {e}")
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get market overview for major indices.
        
        Returns:
            Dictionary with index data
        """
        # Try baostock first
        try:
            return self._get_market_overview_baostock()
        except Exception as e:
            logger.warning(f"BaoStock market overview failed: {e}")
        
        # Try akshare as fallback
        try:
            return self._get_market_overview_akshare()
        except Exception as e:
            logger.warning(f"akshare market overview failed: {e}")
        
        return {}
    
    def _get_market_overview_baostock(self) -> Dict[str, Any]:
        """Get market overview using baostock."""
        import baostock as bs
        
        self._login_baostock()
        
        indices = {
            "shanghai": "sh.000001",  # 上证指数
            "shenzhen": "sz.399001",  # 深证成指
            "chinext": "sz.399006",   # 创业板指
        }
        
        result = {}
        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        for name, code in indices.items():
            try:
                rs = bs.query_history_k_data_plus(
                    code,
                    "date,close,volume",
                    start_date=yesterday,
                    end_date=today,
                    frequency="d",
                    adjustflag="3"
                )
                
                data_list = []
                while (rs.error_code == '0') and rs.next():
                    data_list.append(rs.get_row_data())
                
                if len(data_list) >= 2:
                    df = pd.DataFrame(data_list, columns=rs.fields)
                    latest = df.iloc[-1]
                    prev = df.iloc[-2]
                    
                    price = float(latest['close'])
                    prev_price = float(prev['close'])
                    change = ((price - prev_price) / prev_price) * 100
                    
                    result[name] = {
                        "code": code.split('.')[1],
                        "price": price,
                        "change": round(change, 2),
                        "volume": int(float(latest['volume'])),
                        "date": latest['date']
                    }
            except Exception as e:
                logger.warning(f"Failed to get index {name} via baostock: {e}")
        
        return result
    
    def _get_market_overview_akshare(self) -> Dict[str, Any]:
        """Get market overview using akshare."""
        import akshare as ak
        
        indices = {
            "shanghai": "000001",
            "shenzhen": "399001",
            "chinext": "399006",
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
                logger.warning(f"Failed to get index {name} via akshare: {e}")
        
        return result
    
    def get_stock_list(self) -> List[Dict[str, Any]]:
        """Get list of all A-shares.
        
        Returns:
            List of stock dictionaries
        """
        # Try baostock first
        try:
            stocks = self._get_stock_list_baostock()
            if stocks:
                return stocks
        except Exception as e:
            logger.warning(f"BaoStock stock list failed: {e}")
        
        # Try akshare as fallback
        try:
            return self._get_stock_list_akshare()
        except Exception as e:
            logger.warning(f"akshare stock list failed: {e}")
        
        return []
    
    def _get_stock_list_baostock(self) -> List[Dict[str, Any]]:
        """Get stock list using baostock."""
        import baostock as bs
        
        self._login_baostock()
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get all stocks
        rs = bs.query_stock_basic(code_name="")
        
        stocks = []
        while (rs.error_code == '0') and rs.next():
            row = rs.get_row_data()
            code = row[0]  # e.g., sh.600000
            
            # Get latest quote
            try:
                rs_quote = bs.query_history_k_data_plus(
                    code,
                    "date,close,peTTM,pbMRQ,psTTM,pcfNcfTTM,volume,amount,turn",
                    start_date=(datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
                    end_date=today,
                    frequency="d",
                    adjustflag="3"
                )
                
                quote_data = []
                while (rs_quote.error_code == '0') and rs_quote.next():
                    quote_data.append(rs_quote.get_row_data())
                
                if quote_data:
                    latest = quote_data[-1]
                    price = float(latest[1]) if latest[1] else 0
                    pe = float(latest[2]) if latest[2] else None
                    pb = float(latest[3]) if latest[3] else None
                    volume = float(latest[6]) if latest[6] else 0
                    
                    # Calculate change
                    change = 0
                    if len(quote_data) >= 2:
                        prev_price = float(quote_data[-2][1]) if quote_data[-2][1] else 0
                        if prev_price > 0:
                            change = ((price - prev_price) / prev_price) * 100
                    
                    stock = {
                        "code": code.split('.')[1],
                        "name": row[1] if len(row) > 1 else "",
                        "price": price,
                        "change": round(change, 2),
                        "volume": volume,
                        "amount": float(latest[7]) if latest[7] else 0,
                        "pe": pe,
                        "pb": pb,
                        "sector": "",
                    }
                    stocks.append(stock)
            except Exception:
                pass
            
            # Limit to top 100 stocks for performance
            if len(stocks) >= 100:
                break
        
        logger.info(f"Collected {len(stocks)} stocks via baostock")
        return stocks
    
    def _get_stock_list_akshare(self) -> List[Dict[str, Any]]:
        """Get stock list using akshare."""
        import akshare as ak
        
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
        
        logger.info(f"Collected {len(stocks)} stocks via akshare")
        return stocks
    
    def get_stock_price(self, code: str, period: str = "daily") -> pd.DataFrame:
        """Get historical price data for a stock.
        
        Args:
            code: Stock code
            period: Data period (daily, weekly, monthly)
            
        Returns:
            DataFrame with price data
        """
        try:
            import baostock as bs
            
            self._login_baostock()
            
            # Format code for baostock
            if code.startswith('6'):
                bs_code = f"sh.{code}"
            else:
                bs_code = f"sz.{code}"
            
            today = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            
            frequency = "d" if period == "daily" else ("w" if period == "weekly" else "m")
            
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,open,high,low,close,volume,amount",
                start_date=start_date,
                end_date=today,
                frequency=frequency,
                adjustflag="3"
            )
            
            data_list = []
            while (rs.error_code == '0') and rs.next():
                data_list.append(rs.get_row_data())
            
            if data_list:
                df = pd.DataFrame(data_list, columns=rs.fields)
                for col in ['open', 'high', 'low', 'close', 'volume', 'amount']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
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
            import baostock as bs
            
            self._login_baostock()
            
            # Format code for baostock
            if code.startswith('6'):
                bs_code = f"sh.{code}"
            else:
                bs_code = f"sz.{code}"
            
            # Get profit data
            rs = bs.query_profit_data(code=bs_code, year=2024, quarter=4)
            
            profit_data = []
            while (rs.error_code == '0') and rs.next():
                profit_data.append(rs.get_row_data())
            
            if profit_data:
                row = profit_data[0]
                return {
                    "code": code,
                    "roe": float(row[4]) if row[4] else None,  # roeAvg
                    "gross_margin": float(row[1]) if row[1] else None,  # gpMargin
                    "net_margin": float(row[2]) if row[2] else None,  # npMargin
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
            import baostock as bs
            
            self._login_baostock()
            
            # Get industry classification
            rs = bs.query_stock_industry()
            
            industries = {}
            while (rs.error_code == '0') and rs.next():
                row = rs.get_row_data()
                industry = row[1] if len(row) > 1 else "未知"
                if industry not in industries:
                    industries[industry] = 0
                industries[industry] += 1
            
            sectors = []
            for name, count in sorted(industries.items(), key=lambda x: x[1], reverse=True)[:20]:
                sectors.append({
                    "name": name,
                    "code": "",
                    "change": 0,
                    "volume": 0,
                    "amount": 0,
                    "stock_count": count
                })
            
            return sectors
            
        except Exception as e:
            logger.error(f"Failed to get sector data: {e}")
            return []
    
    def __del__(self):
        """Cleanup baostock connection."""
        self._logout_baostock()
