"""Financial data enricher - fetch and add financial metrics to stock data."""

import time
from typing import List, Dict, Any
from datetime import datetime

import baostock as bs
from loguru import logger


class FinancialEnricher:
    """Enrich stock data with financial metrics from baostock."""
    
    def __init__(self):
        self._logged_in = False
    
    def _login(self):
        if not self._logged_in:
            lg = bs.login()
            if lg.error_code == '0':
                self._logged_in = True
    
    def _logout(self):
        if self._logged_in:
            bs.logout()
            self._logged_in = False
    
    def enrich_stocks(self, stocks: List[Dict[str, Any]], max_stocks: int = 30) -> List[Dict[str, Any]]:
        """Enrich stock list with financial data.
        
        Args:
            stocks: List of stock dictionaries with code, name, price
            max_stocks: Max stocks to enrich (for speed)
            
        Returns:
            Enriched stock list
        """
        self._login()
        
        enriched = []
        count = 0
        
        for stock in stocks[:max_stocks]:
            code = stock.get('code', '')
            if not code:
                continue
            
            try:
                # Format code for baostock
                if code.startswith('6'):
                    bs_code = f"sh.{code}"
                else:
                    bs_code = f"sz.{code}"
                
                # Get profit data (ROE, margins)
                profit = self._get_profit_data(bs_code)
                
                # Get growth data
                growth = self._get_growth_data(bs_code)
                
                # Get balance data
                balance = self._get_balance_data(bs_code)
                
                # Calculate PE from price and EPS
                price = stock.get('price', 0)
                eps = profit.get('epsTTM', 0)
                pe = price / eps if eps and eps > 0 else None
                
                # Merge data
                enriched_stock = {
                    **stock,
                    'pe': pe,
                    'roe': profit.get('roeAvg', 0) * 100 if profit.get('roeAvg') else None,
                    'gross_margin': profit.get('gpMargin', 0) * 100 if profit.get('gpMargin') else None,
                    'net_margin': profit.get('npMargin', 0) * 100 if profit.get('npMargin') else None,
                    'eps': eps,
                    'revenue': profit.get('MBRevenue', 0),
                    'net_profit': profit.get('netProfit', 0),
                    'profit_growth': growth.get('YOYNI', 0) * 100 if growth.get('YOYNI') else None,
                    'revenue_growth': growth.get('YOYPNI', 0) * 100 if growth.get('YOYPNI') else None,
                    'debt_ratio': balance.get('liabilityToAsset', 0) * 100 if balance.get('liabilityToAsset') else None,
                    'current_ratio': balance.get('currentRatio', 0),
                }
                
                enriched.append(enriched_stock)
                count += 1
                
                if count % 10 == 0:
                    logger.info(f"Enriched {count} stocks...")
                
                # Small delay to avoid overwhelming baostock
                time.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"Failed to enrich {code}: {e}")
                enriched.append(stock)  # Keep original data
        
        self._logout()
        logger.info(f"Enriched {count} stocks with financial data")
        return enriched
    
    def _get_profit_data(self, bs_code: str) -> Dict[str, Any]:
        """Get profit data for a stock."""
        try:
            # Try latest quarter
            year = datetime.now().year
            quarter = (datetime.now().month - 1) // 3 + 1
            
            # Go back if current quarter data not available
            for q_offset in range(4):
                q = quarter - q_offset
                y = year
                if q <= 0:
                    q += 4
                    y -= 1
                
                rs = bs.query_profit_data(code=bs_code, year=y, quarter=q)
                while rs.next():
                    row = rs.get_row_data()
                    if row and len(row) > 5:
                        return {
                            'roeAvg': float(row[3]) if row[3] else 0,
                            'npMargin': float(row[4]) if row[4] else 0,
                            'gpMargin': float(row[5]) if row[5] else 0,
                            'netProfit': float(row[6]) if row[6] else 0,
                            'epsTTM': float(row[7]) if row[7] else 0,
                            'MBRevenue': float(row[8]) if row[8] else 0,
                        }
            
            return {}
        except Exception:
            return {}
    
    def _get_growth_data(self, bs_code: str) -> Dict[str, Any]:
        """Get growth data for a stock."""
        try:
            year = datetime.now().year
            quarter = (datetime.now().month - 1) // 3 + 1
            
            for q_offset in range(4):
                q = quarter - q_offset
                y = year
                if q <= 0:
                    q += 4
                    y -= 1
                
                rs = bs.query_growth_data(code=bs_code, year=y, quarter=q)
                while rs.next():
                    row = rs.get_row_data()
                    if row and len(row) > 4:
                        return {
                            'YOYEquity': float(row[3]) if row[3] else 0,
                            'YOYAsset': float(row[4]) if row[4] else 0,
                            'YOYNI': float(row[5]) if row[5] else 0,
                            'YOYEPSBasic': float(row[6]) if row[6] else 0,
                            'YOYPNI': float(row[7]) if row[7] else 0,
                        }
            
            return {}
        except Exception:
            return {}
    
    def _get_balance_data(self, bs_code: str) -> Dict[str, Any]:
        """Get balance sheet data for a stock."""
        try:
            year = datetime.now().year
            quarter = (datetime.now().month - 1) // 3 + 1
            
            for q_offset in range(4):
                q = quarter - q_offset
                y = year
                if q <= 0:
                    q += 4
                    y -= 1
                
                rs = bs.query_balance_data(code=bs_code, year=y, quarter=q)
                while rs.next():
                    row = rs.get_row_data()
                    if row and len(row) > 5:
                        return {
                            'currentRatio': float(row[3]) if row[3] else 0,
                            'quickRatio': float(row[4]) if row[4] else 0,
                            'cashRatio': float(row[5]) if row[5] else 0,
                            'YOYLiability': float(row[6]) if row[6] else 0,
                            'liabilityToAsset': float(row[7]) if row[7] else 0,
                            'assetToEquity': float(row[8]) if row[8] else 0,
                        }
            
            return {}
        except Exception:
            return {}
