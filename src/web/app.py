"""AutoStockAnalyzer Web Dashboard - Flask Application."""

from flask import Flask, render_template, jsonify
from datetime import datetime
import baostock as bs
import requests

app = Flask(__name__)

def get_stock_price(code):
    """Get real-time stock price."""
    try:
        if code.startswith('6'):
            symbol = f"sh{code}"
        else:
            symbol = f"sz{code}"
        
        url = f"https://hq.sinajs.cn/list={symbol}"
        response = requests.get(url, headers={'Referer': 'https://finance.sina.com.cn'}, timeout=5)
        
        if response.status_code == 200:
            data = response.text.split('"')[1].split(',')
            if len(data) > 3:
                return {
                    'price': float(data[3]),
                    'prev_close': float(data[2]) if data[2] else 0,
                    'high': float(data[4]) if data[4] else 0,
                    'low': float(data[5]) if data[5] else 0,
                    'volume': float(data[8]) if len(data) > 8 else 0,
                }
    except:
        pass
    return None

def get_top_stocks():
    """Get TOP 10 recommended stocks."""
    bs.login()
    
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    
    stock_codes = [
        'sz.000100', 'sz.002038', 'sh.600063', 'sh.600076', 'sz.000012',
        'sz.000059', 'sz.000068', 'sz.002023', 'sh.600075', 'sz.002014',
        'sz.002030', 'sh.600073', 'sh.600080', 'sz.000061', 'sz.000089',
        'sz.000060', 'sz.000050', 'sh.600058', 'sz.000066', 'sz.000025',
    ]
    
    candidates = []
    
    for code in stock_codes:
        try:
            rs = bs.query_stock_basic(code=code)
            name = ""
            while (rs.error_code == '0') and rs.next():
                name = rs.get_row_data()[1]
            
            rs = bs.query_history_k_data_plus(
                code, 'date,close,volume,turn',
                start_date=week_ago, end_date=today,
                frequency='d', adjustflag='3'
            )
            
            data = []
            while (rs.error_code == '0') and rs.next():
                data.append(rs.get_row_data())
            
            if len(data) < 3:
                continue
            
            closes = [float(d[1]) for d in data if d[1]]
            turn = float(data[-1][3]) if data[-1][3] else 0
            price = closes[-1]
            
            if price > 15 or price < 3:
                continue
            
            change_1d = ((closes[-1] - closes[-2]) / closes[-2] * 100) if len(closes) >= 2 else 0
            change_3d = ((closes[-1] - closes[-4]) / closes[-4] * 100) if len(closes) >= 4 else 0
            change_5d = ((closes[-1] - closes[-6]) / closes[-6] * 100) if len(closes) >= 6 else 0
            
            # Score
            score = 0
            if change_1d > 5: score += 35
            elif change_1d > 3: score += 25
            elif change_1d > 1: score += 15
            elif change_1d > 0: score += 10
            
            if change_3d > 10: score += 25
            elif change_3d > 5: score += 15
            elif change_3d > 0: score += 10
            
            if change_5d > 15: score += 20
            elif change_5d > 8: score += 15
            elif change_5d > 0: score += 10
            
            if turn > 10: score += 15
            elif turn > 5: score += 10
            
            if score >= 30:
                candidates.append({
                    'code': code.split('.')[1],
                    'name': name,
                    'price': price,
                    'cost_100': price * 100,
                    'change_1d': round(change_1d, 2),
                    'change_3d': round(change_3d, 2),
                    'change_5d': round(change_5d, 2),
                    'turnover': turn,
                    'score': score
                })
        except:
            continue
    
    bs.logout()
    candidates.sort(key=lambda x: -x['score'])
    return candidates[:10]

@app.route('/')
def dashboard():
    """Main dashboard page."""
    # Portfolio
    portfolio = {
        'capital': 1500,
        'holdings': [
            {
                'code': '002038',
                'name': '双鹭药业',
                'buy_price': 6.43,
                'shares': 100,
                'cost': 643,
            }
        ],
        'cash': 857
    }
    
    # Get real-time prices
    for holding in portfolio['holdings']:
        price_data = get_stock_price(holding['code'])
        if price_data:
            holding['current_price'] = price_data['price']
            holding['change'] = price_data['price'] - holding['buy_price']
            holding['change_pct'] = (holding['change'] / holding['buy_price']) * 100
            holding['market_value'] = price_data['price'] * holding['shares']
    
    # Get top recommendations
    recommendations = get_top_stocks()
    
    return render_template('dashboard.html', 
                         portfolio=portfolio,
                         recommendations=recommendations,
                         now=datetime.now())

@app.route('/api/portfolio')
def api_portfolio():
    """API endpoint for portfolio data."""
    portfolio = {
        'capital': 1500,
        'holdings': [
            {
                'code': '002038',
                'name': '双鹭药业',
                'buy_price': 6.43,
                'shares': 100,
                'cost': 643,
            }
        ],
        'cash': 857
    }
    
    for holding in portfolio['holdings']:
        price_data = get_stock_price(holding['code'])
        if price_data:
            holding['current_price'] = price_data['price']
            holding['change'] = price_data['price'] - holding['buy_price']
            holding['change_pct'] = (holding['change'] / holding['buy_price']) * 100
    
    return jsonify(portfolio)

@app.route('/api/recommendations')
def api_recommendations():
    """API endpoint for stock recommendations."""
    recommendations = get_top_stocks()
    return jsonify(recommendations)

if __name__ == '__main__':
    from datetime import timedelta
    app.run(debug=True, host='0.0.0.0', port=5000)
