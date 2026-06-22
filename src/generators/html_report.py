"""HTML report generator module."""

from typing import Dict, Any
from datetime import datetime
from pathlib import Path

from jinja2 import Template
from loguru import logger


class HTMLReportGenerator:
    """Generate HTML analysis reports."""
    
    def __init__(self):
        """Initialize HTML report generator."""
        self.template_dir = Path(__file__).parent / "templates"
    
    def generate(self, analysis_results: Dict[str, Any]) -> str:
        """Generate HTML report from analysis results.
        
        Args:
            analysis_results: Analysis results dictionary
            
        Returns:
            Path to generated report
        """
        try:
            # Create output directory
            output_dir = Path("./reports")
            output_dir.mkdir(exist_ok=True)
            
            # Generate filename
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}-report.html"
            output_path = output_dir / filename
            
            # Generate HTML content
            html_content = self._render_html(analysis_results)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Report generated: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise
    
    def _render_html(self, data: Dict[str, Any]) -> str:
        """Render HTML template with data."""
        
        template_str = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AutoStockAnalyzer - 每日分析报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
        header p {
            opacity: 0.9;
        }
        .section {
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .market-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }
        .index-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .index-card h3 {
            font-size: 1em;
            color: #666;
            margin-bottom: 10px;
        }
        .index-card .price {
            font-size: 1.5em;
            font-weight: bold;
        }
        .index-card .change {
            font-size: 1.2em;
            margin-top: 5px;
        }
        .positive { color: #e74c3c; }
        .negative { color: #27ae60; }
        .neutral { color: #7f8c8d; }
        .news-list {
            max-height: 400px;
            overflow-y: auto;
        }
        .news-item {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        .news-item:last-child {
            border-bottom: none;
        }
        .news-item h4 {
            margin-bottom: 5px;
        }
        .news-item .meta {
            font-size: 0.9em;
            color: #666;
        }
        .recommendations {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .stock-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .stock-card h4 {
            margin-bottom: 10px;
        }
        .stock-card .score {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .stock-card .details {
            margin-top: 10px;
            font-size: 0.9em;
        }
        .portfolio-strategy {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
        }
        .portfolio-strategy h3 {
            margin-bottom: 15px;
        }
        .position-list {
            list-style: none;
        }
        .position-list li {
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.2);
        }
        .position-list li:last-child {
            border-bottom: none;
        }
        .risk-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: bold;
        }
        .risk-low { background: #27ae60; color: white; }
        .risk-medium { background: #f39c12; color: white; }
        .risk-high { background: #e74c3c; color: white; }
        footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>AutoStockAnalyzer 每日分析报告</h1>
            <p>日期: {{ date }} | 分析时间: {{ analysis_time }}</p>
        </header>
        
        <section class="section">
            <h2>市场概览</h2>
            <div class="market-overview">
                {% for index, data in market_overview.items() %}
                <div class="index-card">
                    <h3>{{ index }}</h3>
                    <div class="price">{{ data.price|default('N/A') }}</div>
                    <div class="change {{ 'positive' if data.change > 0 else 'negative' if data.change < 0 else 'neutral' }}">
                        {{ '%+.2f'|format(data.change|default(0)) }}%
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <section class="section">
            <h2>市场情绪</h2>
            <p><strong>整体情绪:</strong> {{ market_sentiment.overall }}</p>
            <p><strong>情绪评分:</strong> {{ market_sentiment.score }}/10</p>
            {% if market_sentiment.factors %}
            <p><strong>影响因素:</strong> {{ market_sentiment.factors|join(', ') }}</p>
            {% endif %}
        </section>
        
        <section class="section">
            <h2>风险评估</h2>
            <p><strong>风险等级:</strong> <span class="risk-badge risk-{{ risk_level.level }}">{{ risk_level.level }}</span></p>
            <p><strong>风险评分:</strong> {{ risk_level.score }}/10</p>
            {% if risk_level.factors %}
            <p><strong>风险因素:</strong> {{ risk_level.factors|join(', ') }}</p>
            {% endif %}
        </section>
        
        <section class="section">
            <h2>新闻分析</h2>
            <p>共收集 {{ news_impact.total_news }} 条新闻</p>
            <p>正面: {{ news_impact.positive }} | 中性: {{ news_impact.neutral }} | 负面: {{ news_impact.negative }}</p>
            
            <h3 style="margin-top: 20px; margin-bottom: 15px;">重要新闻</h3>
            <div class="news-list">
                {% for news in news_impact.top_impact %}
                <div class="news-item">
                    <h4>{{ news.title }}</h4>
                    <p class="meta">{{ news.source }} | {{ news.time }}</p>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <section class="section">
            <h2>社会热点</h2>
            <p>共收集 {{ social_impact.total_topics }} 个热点话题</p>
            <p>财经相关: {{ social_impact.finance_related }} 个</p>
            
            <h3 style="margin-top: 20px; margin-bottom: 15px;">热门话题</h3>
            <div class="news-list">
                {% for topic in social_impact.top_topics %}
                <div class="news-item">
                    <h4>{{ topic.topic }}</h4>
                    <p class="meta">平台: {{ topic.platform }} | 热度: {{ topic.heat }}</p>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <section class="section">
            <h2>政策影响</h2>
            <p>共收集 {{ policy_impact.total_policies }} 条政策</p>
            <p>高影响政策: {{ policy_impact.high_impact }} 条</p>
            <p>受影响行业: {{ policy_impact.sectors_affected|join(', ') }}</p>
            
            <h3 style="margin-top: 20px; margin-bottom: 15px;">重要政策</h3>
            <div class="news-list">
                {% for policy in policy_impact.top_policies %}
                <div class="news-item">
                    <h4>{{ policy.title }}</h4>
                    <p class="meta">来源: {{ policy.source }} | 影响评分: {{ policy.impact_score }}</p>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <section class="section">
            <h2>科研动态</h2>
            <p>共收集 {{ research_impact.total_papers }} 篇论文/资讯</p>
            <p>高影响研究: {{ research_impact.high_impact }} 篇</p>
            <p>涉及领域: {{ research_impact.fields_covered|join(', ') }}</p>
            
            <h3 style="margin-top: 20px; margin-bottom: 15px;">重要研究</h3>
            <div class="news-list">
                {% for paper in research_impact.top_papers %}
                <div class="news-item">
                    <h4>{{ paper.title }}</h4>
                    <p class="meta">来源: {{ paper.source }} | 影响评分: {{ paper.impact_score }}</p>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <section class="section">
            <h2>板块分析</h2>
            <h3 style="margin-bottom: 15px;">表现最佳板块</h3>
            <div class="market-overview">
                {% for sector, data in sector_analysis.top_sectors.items() %}
                <div class="index-card">
                    <h3>{{ sector }}</h3>
                    <div class="change {{ 'positive' if data.avg_change > 0 else 'negative' if data.avg_change < 0 else 'neutral' }}">
                        {{ '%+.2f'|format(data.avg_change) }}%
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <section class="section">
            <h2>股票推荐</h2>
            <div class="recommendations">
                {% for rec in recommendations %}
                <div class="stock-card">
                    <h4>{{ rec.name }} ({{ rec.code }})</h4>
                    <div class="score">{{ rec.score }}</div>
                    <div class="details">
                        <p>现价: ¥{{ rec.price }} | 涨跌: {{ '%+.2f'|format(rec.change) }}%</p>
                        <p>建议操作: <strong>{{ rec.action }}</strong></p>
                        <p>风险等级: <span class="risk-badge risk-{{ rec.risk }}">{{ rec.risk }}</span></p>
                        <p>预期收益: {{ rec.expected_return }}</p>
                        <p>{{ rec.reason }}</p>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <section class="section">
            <h2>投资组合建议 (1000元本金)</h2>
            <div class="portfolio-strategy">
                <h3>资金配置方案</h3>
                <p>总资金: ¥{{ portfolio_strategy.capital }}</p>
                <p>已分配: ¥{{ portfolio_strategy.allocated }}</p>
                <p>现金保留: ¥{{ portfolio_strategy.cash_remaining }}</p>
                
                {% if portfolio_strategy.positions %}
                <h3 style="margin-top: 20px;">推荐持仓</h3>
                <ul class="position-list">
                    {% for pos in portfolio_strategy.positions %}
                    <li>
                        <strong>{{ pos.name }}</strong> ({{ pos.code }})<br>
                        现价: ¥{{ pos.price }} | 数量: {{ pos.shares }}股<br>
                        成本: ¥{{ pos.cost }} | 占比: {{ pos.allocation }}%<br>
                        <small>{{ pos.reason }}</small>
                    </li>
                    {% endfor %}
                </ul>
                {% endif %}
                
                <p style="margin-top: 20px;"><strong>策略总结:</strong> {{ portfolio_strategy.summary }}</p>
            </div>
        </section>
        
        {% if mainboard_stocks %}
        <section class="section">
            <h2>主板股票筛选 (激进策略)</h2>
            <p>筛选条件: 主板 | 价格5-19元 | 高动量 | 适合小资金</p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <thead>
                    <tr style="background: #f8f9fa;">
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #667eea;">代码</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #667eea;">名称</th>
                        <th style="padding: 10px; text-align: right; border-bottom: 2px solid #667eea;">价格</th>
                        <th style="padding: 10px; text-align: right; border-bottom: 2px solid #667eea;">1手成本</th>
                        <th style="padding: 10px; text-align: right; border-bottom: 2px solid #667eea;">今日涨跌</th>
                        <th style="padding: 10px; text-align: center; border-bottom: 2px solid #667eea;">评分</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in mainboard_stocks[:10] %}
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px;">{{ stock.code }}</td>
                        <td style="padding: 10px;">{{ stock.name }}</td>
                        <td style="padding: 10px; text-align: right;">¥{{ "%.2f"|format(stock.price) }}</td>
                        <td style="padding: 10px; text-align: right;">¥{{ "%.0f"|format(stock.cost_100) }}</td>
                        <td style="padding: 10px; text-align: right; color: {{ '#e74c3c' if stock.change > 0 else '#27ae60' }};">
                            {{ "%+.2f"|format(stock.change) }}%
                        </td>
                        <td style="padding: 10px; text-align: center;">
                            <span style="background: #667eea; color: white; padding: 3px 8px; border-radius: 10px;">{{ stock.score }}</span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </section>
        
        <section class="section">
            <h2>今日买入方案</h2>
            <div class="portfolio-strategy">
                <h3>激进策略 - 100股起买</h3>
                <p>总预算: ¥{{ buy_plan.budget }}</p>
                <p>总投入: ¥{{ buy_plan.total_cost }}</p>
                <p>剩余资金: ¥{{ buy_plan.remaining }}</p>
                
                {% if buy_plan.positions %}
                <h3 style="margin-top: 20px;">推荐买入</h3>
                <ul class="position-list">
                    {% for pos in buy_plan.positions %}
                    <li>
                        <strong>{{ pos.name }}</strong> ({{ pos.code }})<br>
                        价格: ¥{{ "%.2f"|format(pos.price) }} × 100股 = ¥{{ "%.0f"|format(pos.cost) }}<br>
                        涨跌: {{ "%+.2f"|format(pos.change) }}% | 评分: {{ pos.score }}
                    </li>
                    {% endfor %}
                </ul>
                {% endif %}
                
                <p style="margin-top: 20px;"><strong>操作建议:</strong> {{ buy_plan.summary }}</p>
            </div>
        </section>
        {% endif %}
        
        <footer>
            <p>声明: 本报告仅供参考，不构成投资建议。股市有风险，投资需谨慎。</p>
            <p>AutoStockAnalyzer v1.0 | 生成时间: {{ analysis_time }}</p>
        </footer>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        return template.render(data)
