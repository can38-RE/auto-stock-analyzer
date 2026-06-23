"""Portfolio tracker module for managing stock holdings."""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from loguru import logger


class PortfolioTracker:
    """Track and manage stock portfolio."""
    
    def __init__(self, portfolio_file: str = "data/portfolio.json"):
        """Initialize portfolio tracker."""
        self.portfolio_file = Path(portfolio_file)
        self.portfolio_file.parent.mkdir(exist_ok=True)
        self.portfolio = self._load_portfolio()
    
    def _load_portfolio(self) -> Dict[str, Any]:
        """Load portfolio from file."""
        if self.portfolio_file.exists():
            with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Default portfolio structure
        return {
            "capital": 1900,
            "holdings": [],
            "transactions": [],
            "updated_at": datetime.now().isoformat()
        }
    
    def _save_portfolio(self):
        """Save portfolio to file."""
        self.portfolio["updated_at"] = datetime.now().isoformat()
        with open(self.portfolio_file, 'w', encoding='utf-8') as f:
            json.dump(self.portfolio, f, ensure_ascii=False, indent=2)
    
    def add_holding(self, code: str, name: str, price: float, shares: int, 
                    buy_date: str = None) -> bool:
        """Add a stock holding."""
        if buy_date is None:
            buy_date = datetime.now().strftime("%Y-%m-%d")
        
        # Check if already holding
        for h in self.portfolio["holdings"]:
            if h["code"] == code:
                # Update existing holding
                total_cost = h["cost"] * h["shares"] + price * shares
                total_shares = h["shares"] + shares
                h["avg_price"] = total_cost / total_shares
                h["shares"] = total_shares
                h["cost"] = round(h["avg_price"], 2)
                
                self.portfolio["transactions"].append({
                    "type": "buy",
                    "code": code,
                    "name": name,
                    "price": price,
                    "shares": shares,
                    "date": buy_date,
                    "total": price * shares
                })
                self._save_portfolio()
                logger.info(f"Updated holding: {code} {name}, now {total_shares} shares")
                return True
        
        # New holding
        holding = {
            "code": code,
            "name": name,
            "price": price,
            "cost": price,
            "shares": shares,
            "buy_date": buy_date,
            "avg_price": price
        }
        self.portfolio["holdings"].append(holding)
        
        self.portfolio["transactions"].append({
            "type": "buy",
            "code": code,
            "name": name,
            "price": price,
            "shares": shares,
            "date": buy_date,
            "total": price * shares
        })
        
        self._save_portfolio()
        logger.info(f"Added holding: {code} {name}, {shares} shares at {price}")
        return True
    
    def remove_holding(self, code: str, sell_price: float, shares: int = None,
                       sell_date: str = None) -> bool:
        """Remove or reduce a stock holding."""
        if sell_date is None:
            sell_date = datetime.now().strftime("%Y-%m-%d")
        
        for i, h in enumerate(self.portfolio["holdings"]):
            if h["code"] == code:
                if shares is None or shares >= h["shares"]:
                    # Sell all
                    pnl = (sell_price - h["cost"]) * h["shares"]
                    pnl_pct = ((sell_price - h["cost"]) / h["cost"]) * 100
                    
                    self.portfolio["transactions"].append({
                        "type": "sell",
                        "code": code,
                        "name": h["name"],
                        "price": sell_price,
                        "shares": h["shares"],
                        "date": sell_date,
                        "total": sell_price * h["shares"],
                        "pnl": round(pnl, 2),
                        "pnl_pct": round(pnl_pct, 2)
                    })
                    
                    self.portfolio["holdings"].pop(i)
                    logger.info(f"Sold all {code}: {pnl:+.2f}元 ({pnl_pct:+.2f}%)")
                else:
                    # Sell partial
                    pnl = (sell_price - h["cost"]) * shares
                    pnl_pct = ((sell_price - h["cost"]) / h["cost"]) * 100
                    
                    self.portfolio["transactions"].append({
                        "type": "sell",
                        "code": code,
                        "name": h["name"],
                        "price": sell_price,
                        "shares": shares,
                        "date": sell_date,
                        "total": sell_price * shares,
                        "pnl": round(pnl, 2),
                        "pnl_pct": round(pnl_pct, 2)
                    })
                    
                    h["shares"] -= shares
                    logger.info(f"Sold {shares} shares of {code}: {pnl:+.2f}元")
                
                self._save_portfolio()
                return True
        
        logger.warning(f"Holding {code} not found")
        return False
    
    def get_holdings(self) -> List[Dict[str, Any]]:
        """Get all current holdings."""
        return self.portfolio["holdings"]
    
    def get_transactions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent transactions."""
        return self.portfolio["transactions"][-limit:]
    
    def get_portfolio_summary(self, current_prices: Dict[str, float] = None) -> Dict[str, Any]:
        """Get portfolio summary with current values."""
        holdings = self.portfolio["holdings"]
        capital = self.portfolio["capital"]
        
        total_cost = sum(h["cost"] * h["shares"] for h in holdings)
        total_value = 0
        total_pnl = 0
        
        holding_details = []
        for h in holdings:
            code = h["code"]
            current_price = current_prices.get(code, h["price"]) if current_prices else h["price"]
            value = current_price * h["shares"]
            cost = h["cost"] * h["shares"]
            pnl = value - cost
            pnl_pct = ((current_price - h["cost"]) / h["cost"]) * 100 if h["cost"] > 0 else 0
            
            total_value += value
            total_pnl += pnl
            
            holding_details.append({
                "code": code,
                "name": h["name"],
                "shares": h["shares"],
                "cost": h["cost"],
                "current_price": current_price,
                "value": round(value, 2),
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl_pct, 2)
            })
        
        cash = capital - total_cost
        
        return {
            "capital": capital,
            "total_cost": round(total_cost, 2),
            "total_value": round(total_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round((total_pnl / total_cost) * 100, 2) if total_cost > 0 else 0,
            "cash": round(cash, 2),
            "holdings_count": len(holdings),
            "holdings": holding_details
        }
    
    def update_capital(self, new_capital: float):
        """Update total capital."""
        self.portfolio["capital"] = new_capital
        self._save_portfolio()
        logger.info(f"Capital updated to {new_capital}")


def format_portfolio_summary(summary: Dict[str, Any]) -> str:
    """Format portfolio summary as readable text."""
    lines = [
        "=" * 60,
        "持仓汇总",
        "=" * 60,
        f"总资金: {summary['capital']}元",
        f"持仓成本: {summary['total_cost']}元",
        f"持仓市值: {summary['total_value']}元",
        f"总盈亏: {summary['total_pnl']:+.2f}元 ({summary['total_pnl_pct']:+.2f}%)",
        f"可用现金: {summary['cash']}元",
        f"持股数量: {summary['holdings_count']}只",
        "",
        "持仓明细:",
        "-" * 60,
    ]
    
    for h in summary['holdings']:
        lines.append(f"{h['code']} {h['name']}: {h['shares']}股")
        lines.append(f"  成本: {h['cost']}元 | 现价: {h['current_price']}元")
        lines.append(f"  市值: {h['value']}元 | 盈亏: {h['pnl']:+.2f}元 ({h['pnl_pct']:+.2f}%)")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)
