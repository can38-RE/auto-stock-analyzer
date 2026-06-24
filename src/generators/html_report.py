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
            <h1>{{ session_label|default('早盘') }}分析报告</h1>
            <p>日期: {{ date }} | 分析时间: {{ analysis_time }} | 时段: {{ session_label|default('早盘') }}</p>
            {% if session == 'morning' %}
            <p style="font-size: 0.9em; opacity: 0.9;">早盘策略: 为9:30开盘做准备，关注隔夜消息和全球市场</p>
            {% else %}
            <p style="font-size: 0.9em; opacity: 0.9;">午盘策略: 关注上午走势，为14:30午后交易做准备</p>
            {% endif %}
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
            <p><strong>风险等级:</strong> 
                <span class="risk-badge risk-{{ risk_level.level }}">
                    {% if risk_level.level == 'high' %}高风险{% elif risk_level.level == 'medium' %}中等风险{% else %}低风险{% endif %}
                </span>
            </p>
            <p><strong>风险评分:</strong> {{ risk_level.score }}/10</p>
            {% if risk_level.factors %}
            <p><strong>风险因素:</strong> {{ risk_level.factors|join(', ') }}</p>
            {% endif %}
        </section>
        
        {% if session == 'morning' %}
        <section class="section" style="border-left: 4px solid #667eea;">
            <h2>早盘策略 (9:30开盘前)</h2>
            <div style="background: #e8f5e9; padding: 15px; border-radius: 8px;">
                <h3>开盘前准备</h3>
                <ul>
                    <li>关注隔夜美股和全球市场走势</li>
                    <li>查看今日重要经济数据发布时间</li>
                    <li>确认目标股票的开盘价位置</li>
                    <li>设置好止损单，控制风险</li>
                </ul>
            </div>
            <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin-top: 10px;">
                <h3>早盘买入时机</h3>
                <ul>
                    <li><strong>开盘急跌:</strong> 观察是否是洗盘，等企稳后买入</li>
                    <li><strong>高开:</strong> 等回调到支撑位再买，不要追高</li>
                    <li><strong>平开:</strong> 关注前30分钟走势，确认方向</li>
                </ul>
            </div>
        </section>
        {% else %}
        <section class="section" style="border-left: 4px solid #ff9800;">
            <h2>午盘策略 (14:30午后交易)</h2>
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px;">
                <h3>上午走势回顾</h3>
                <ul>
                    <li>分析上午大盘和个股表现</li>
                    <li>确认早盘买入的股票是否按预期运行</li>
                    <li>观察成交量变化和资金流向</li>
                </ul>
            </div>
            <div style="background: #fce4ec; padding: 15px; border-radius: 8px; margin-top: 10px;">
                <h3>午后操作建议</h3>
                <ul>
                    <li><strong>上午强势:</strong> 可继续持有或加仓</li>
                    <li><strong>上午弱势:</strong> 考虑减仓或止损</li>
                    <li><strong>尾盘拉升:</strong> 注意是否是诱多，谨慎追涨</li>
                    <li><strong>尾盘跳水:</strong> 可能是抄底机会，但要确认支撑</li>
                </ul>
            </div>
        </section>
        {% endif %}
        
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
                        <p>风险等级: <span class="risk-badge risk-{{ rec.risk }}">
                            {% if rec.risk == 'low' %}低风险{% elif rec.risk == 'medium' %}中等风险{% elif rec.risk == 'high' %}高风险{% else %}{{ rec.risk }}{% endif %}
                        </span></p>
                        <p>预期收益: {{ rec.expected_return }}</p>
                        <p>{{ rec.reason }}</p>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <section class="section">
            <h2>投资组合建议 (1900元本金)</h2>
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
        
        {% if portfolio %}
        <section class="section">
            <h2>我的持仓</h2>
            <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
                <div style="flex: 1; min-width: 150px; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <p><strong>总资金</strong></p>
                    <p style="font-size: 1.5em; color: #667eea;">¥{{ portfolio.capital }}</p>
                </div>
                <div style="flex: 1; min-width: 150px; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <p><strong>持仓市值</strong></p>
                    <p style="font-size: 1.5em;">¥{{ portfolio.total_value }}</p>
                </div>
                <div style="flex: 1; min-width: 150px; background: {{ '#e8f5e9' if portfolio.total_pnl >= 0 else '#ffebee' }}; padding: 15px; border-radius: 8px;">
                    <p><strong>总盈亏</strong></p>
                    <p style="font-size: 1.5em; color: {{ '#e74c3c' if portfolio.total_pnl < 0 else '#27ae60' }};">
                        {{ "%+.2f"|format(portfolio.total_pnl) }}元
                    </p>
                    <p>({{ "%+.2f"|format(portfolio.total_pnl_pct) }}%)</p>
                </div>
                <div style="flex: 1; min-width: 150px; background: #f8f9fa; padding: 15px; border-radius: 8px;">
                    <p><strong>可用现金</strong></p>
                    <p style="font-size: 1.5em;">¥{{ portfolio.cash }}</p>
                </div>
            </div>
            
            {% if portfolio.holdings %}
            <h3>持仓明细</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <thead>
                    <tr style="background: #667eea; color: white;">
                        <th style="padding: 12px; text-align: left;">股票</th>
                        <th style="padding: 12px; text-align: center;">持股</th>
                        <th style="padding: 12px; text-align: right;">成本</th>
                        <th style="padding: 12px; text-align: right;">现价</th>
                        <th style="padding: 12px; text-align: right;">市值</th>
                        <th style="padding: 12px; text-align: right;">盈亏</th>
                    </tr>
                </thead>
                <tbody>
                    {% for h in portfolio.holdings %}
                    <tr style="border-bottom: 1px solid #eee; background: {{ '#ffebee' if h.pnl < 0 else '#e8f5e9' }};">
                        <td style="padding: 10px;">
                            <strong>{{ h.name }}</strong><br>
                            <small>{{ h.code }}</small>
                        </td>
                        <td style="padding: 10px; text-align: center;">{{ h.shares }}股</td>
                        <td style="padding: 10px; text-align: right;">¥{{ "%.2f"|format(h.cost) }}</td>
                        <td style="padding: 10px; text-align: right;">¥{{ "%.2f"|format(h.current_price) }}</td>
                        <td style="padding: 10px; text-align: right;">¥{{ "%.2f"|format(h.value) }}</td>
                        <td style="padding: 10px; text-align: right; color: {{ '#e74c3c' if h.pnl < 0 else '#27ae60' }};">
                            {{ "%+.2f"|format(h.pnl) }}元<br>
                            <small>({{ "%+.2f"|format(h.pnl_pct) }}%)</small>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
            
            {% if portfolio.holdings_count == 0 %}
            <p style="text-align: center; color: #666; padding: 20px;">暂无持仓</p>
            {% endif %}
        </section>
        {% endif %}
        
        {% if chokepoint_analysis %}
        <section class="section">
            <h2>Serenity瓶颈理论分析</h2>
            <p style="font-style: italic; color: #666;">"Own the bottleneck, not the brand" - @aleabitoreddit</p>
            <p>寻找AI供应链中不可替代的瓶颈环节，而非追逐热门品牌</p>
            
            <h3 style="margin-top: 20px; margin-bottom: 15px;">三阶段轮动策略</h3>
            <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                <div style="flex: 1; min-width: 200px; background: #f0f0f0; padding: 15px; border-radius: 8px;">
                    <strong>Phase 1 (已完成)</strong><br>
                    内存/HBM<br>
                    <small>机构已入场</small>
                </div>
                <div style="flex: 1; min-width: 200px; background: #667eea; color: white; padding: 15px; border-radius: 8px;">
                    <strong>Phase 2 (当前) ⬅️</strong><br>
                    光收发器<br>
                    <small>当前主战场</small>
                </div>
                <div style="flex: 1; min-width: 200px; background: #e8f5e9; padding: 15px; border-radius: 8px;">
                    <strong>Phase 3 (新兴)</strong><br>
                    SiPh/CPO<br>
                    <small>2027-2028拐点</small>
                </div>
            </div>
            
            <h3 style="margin-top: 25px; margin-bottom: 15px;">AI供应链瓶颈图谱</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f8f9fa;">
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #667eea;">层级</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #667eea;">环节</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #667eea;">A股标的</th>
                        <th style="padding: 10px; text-align: left; border-bottom: 2px solid #667eea;">核心逻辑</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in chokepoint_analysis.stocks[:10] %}
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px;">{{ stock.layer_description }}</td>
                        <td style="padding: 10px;">{{ stock.importance }}</td>
                        <td style="padding: 10px;"><strong>{{ stock.code }}</strong> {{ stock.name }}</td>
                        <td style="padding: 10px;">{{ stock.reason }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </section>
        {% endif %}
        
        {% if mainboard_stocks %}
        {% if top_stocks %}
        <section class="section">
            <h2>综合评分TOP10</h2>
            <p>评分权重: 技术面25% | 基本面25% | 政策面20% | 流动性15% | 价格位10% | 玄学5%</p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                <thead>
                    <tr style="background: #667eea; color: white;">
                        <th style="padding: 12px; text-align: center;">排名</th>
                        <th style="padding: 12px; text-align: left;">股票</th>
                        <th style="padding: 12px; text-align: right;">价格</th>
                        <th style="padding: 12px; text-align: right;">1手成本</th>
                        <th style="padding: 12px; text-align: right;">5日涨幅</th>
                        <th style="padding: 12px; text-align: center;">综合评分</th>
                        <th style="padding: 12px; text-align: center;">建议持仓</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in top_stocks %}
                    <tr style="border-bottom: 1px solid #eee; background: {{ '#e8f5e9' if loop.index <= 3 else '#fff' }};">
                        <td style="padding: 10px; text-align: center; font-weight: bold;">{{ loop.index }}</td>
                        <td style="padding: 10px;">
                            <strong>{{ stock.name }}</strong><br>
                            <small>{{ stock.code }}</small>
                        </td>
                        <td style="padding: 10px; text-align: right;">¥{{ "%.2f"|format(stock.price) }}</td>
                        <td style="padding: 10px; text-align: right;">¥{{ "%.0f"|format(stock.cost_100) }}</td>
                        <td style="padding: 10px; text-align: right; color: {{ '#e74c3c' if stock.change_5d > 0 else '#27ae60' }};">
                            {{ "%+.2f"|format(stock.change_5d) }}%
                        </td>
                        <td style="padding: 10px; text-align: center;">
                            <span style="background: {{ '#27ae60' if stock.total_score >= 70 else '#f39c12' if stock.total_score >= 60 else '#e74c3c' }}; color: white; padding: 5px 10px; border-radius: 15px; font-weight: bold;">
                                {{ "%.1f"|format(stock.total_score) }}
                            </span>
                        </td>
                        <td style="padding: 10px; text-align: center;">{{ stock.holding }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 8px;">
                <h4>评分维度详情</h4>
                {% for stock in top_stocks[:3] %}
                <div style="margin-top: 10px; padding: 10px; background: white; border-radius: 5px;">
                    <strong>{{ stock.name }} ({{ stock.code }})</strong>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 5px;">
                        <span>技术面: {{ stock.technical_score }}</span>
                        <span>基本面: {{ stock.fundamental_score }}</span>
                        <span>政策面: {{ stock.policy_score }}</span>
                        <span>流动性: {{ stock.volume_score }}</span>
                        <span>价格位: {{ stock.price_score }}</span>
                        <span>玄学: {{ stock.metaphysics_score }}</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </section>
        {% endif %}
        
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
        
        {% if trend_analysis %}
        <section class="section">
            <h2>走势分析 + 入场策略</h2>
            <p>T+1规则：今天买入，明天才能卖出。根据趋势选择不同入场策略。</p>
            
            <!-- 总结表格 -->
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 25px;">
                <thead>
                    <tr style="background: #667eea; color: white;">
                        <th style="padding: 12px; text-align: left;">股票</th>
                        <th style="padding: 12px; text-align: center;">趋势</th>
                        <th style="padding: 12px; text-align: center;">策略</th>
                        <th style="padding: 12px; text-align: right;">入场价</th>
                        <th style="padding: 12px; text-align: right;">止损</th>
                        <th style="padding: 12px; text-align: right;">止盈</th>
                        <th style="padding: 12px; text-align: center;">建议持仓</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in trend_analysis %}
                    <tr style="border-bottom: 1px solid #eee; background: {{ '#e8f5e9' if stock.trend.direction in ['strong_uptrend', 'uptrend'] else '#ffebee' if stock.trend.direction in ['downtrend', 'strong_downtrend'] else '#fff8e1' }};">
                        <td style="padding: 10px;">
                            <strong>{{ stock.name }}</strong><br>
                            <small>{{ stock.code }} | ¥{{ "%.2f"|format(stock.current_price) }}</small>
                        </td>
                        <td style="padding: 10px; text-align: center;">
                            {{ stock.trend.description }}
                        </td>
                        <td style="padding: 10px; text-align: center;">
                            <strong>{{ stock.strategy.type }}</strong>
                        </td>
                        <td style="padding: 10px; text-align: right;">
                            ¥{{ "%.2f"|format(stock.strategy.entry_price) }}
                        </td>
                        <td style="padding: 10px; text-align: right; color: #e74c3c;">
                            ¥{{ "%.2f"|format(stock.entry_prices.stop_loss) }}
                        </td>
                        <td style="padding: 10px; text-align: right; color: #27ae60;">
                            ¥{{ "%.2f"|format(stock.entry_prices.take_profit_1) }}
                        </td>
                        <td style="padding: 10px; text-align: center;">
                            <strong>{{ stock.holding.period }}</strong>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <!-- 详细分析 -->
            {% for stock in trend_analysis %}
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 15px; border-left: 4px solid {{ '#27ae60' if stock.trend.direction in ['strong_uptrend', 'uptrend'] else '#e74c3c' if stock.trend.direction in ['downtrend', 'strong_downtrend'] else '#f39c12' }};">
                <h3>{{ stock.name }} ({{ stock.code }})</h3>
                <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 10px;">
                    <div style="flex: 1; min-width: 150px;">
                        <p><strong>当前价:</strong> ¥{{ "%.2f"|format(stock.current_price) }}</p>
                        <p><strong>今日涨跌:</strong> <span style="color: {{ '#e74c3c' if stock.today_change > 0 else '#27ae60' }}">{{ "%+.2f"|format(stock.today_change) }}%</span></p>
                    </div>
                    <div style="flex: 1; min-width: 150px;">
                        <p><strong>趋势:</strong> {{ stock.trend.description }}</p>
                        <p><strong>MA5/10/20:</strong> {{ stock.trend.ma5 }}/{{ stock.trend.ma10 }}/{{ stock.trend.ma20 }}</p>
                    </div>
                    <div style="flex: 1; min-width: 150px;">
                        <p><strong>支撑:</strong> ¥{{ stock.support_resistance.support }}</p>
                        <p><strong>阻力:</strong> ¥{{ stock.support_resistance.resistance }}</p>
                    </div>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <h4 style="color: #667eea;">{{ stock.strategy.type }}</h4>
                    <p><strong>建议动作:</strong> {{ stock.strategy.action }}</p>
                    <p><strong>入场价:</strong> ¥{{ "%.2f"|format(stock.strategy.entry_price) }}</p>
                    <p><strong>风险等级:</strong> 
                        {% if stock.strategy.risk_level == 'low' %}低风险{% elif stock.strategy.risk_level == 'medium' %}中等风险{% elif stock.strategy.risk_level == 'high' %}高风险{% else %}{{ stock.strategy.risk_level }}{% endif %}
                    </p>
                    
                    <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin-top: 15px;">
                        <h4 style="color: #1565c0; margin-bottom: 10px;">持仓时间建议</h4>
                        <p><strong>建议持仓:</strong> {{ stock.holding.period|default('1-3天') }}</p>
                        <p><strong>操作策略:</strong> {{ stock.holding.strategy|default('根据走势决定') }}</p>
                        <p><strong>波动率:</strong> {{ stock.holding.volatility|default(0) }}%</p>
                        {% if stock.holding.sell_signals is defined and stock.holding.sell_signals %}
                        <p style="margin-top: 10px;"><strong>卖出信号:</strong></p>
                        <ul style="margin: 5px 0; padding-left: 20px;">
                            {% for signal in stock.holding.sell_signals[:3] %}
                            <li>{{ signal }}</li>
                            {% endfor %}
                        </ul>
                        {% endif %}
                    </div>
                    
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px;">
                        <div style="flex: 1; min-width: 120px;">
                            <p><strong>激进入场:</strong> ¥{{ "%.2f"|format(stock.entry_prices.aggressive) }}</p>
                            <p><strong>稳健入场:</strong> ¥{{ "%.2f"|format(stock.entry_prices.moderate) }}</p>
                        </div>
                        <div style="flex: 1; min-width: 120px;">
                            <p><strong>止损:</strong> ¥{{ "%.2f"|format(stock.entry_prices.stop_loss) }} (-7%)</p>
                            <p><strong>止盈1:</strong> ¥{{ "%.2f"|format(stock.entry_prices.take_profit_1) }} (+10%)</p>
                        </div>
                    </div>
                    
                    <ul style="margin-top: 10px; padding-left: 20px;">
                        {% for tip in stock.strategy.tips %}
                        <li>{{ tip }}</li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            {% endfor %}
        </section>
        {% endif %}
        
        {% if metaphysics %}
        <section class="section" style="border-left: 4px solid #9c27b0;">
            <h2>玄学分析 (仅供参考)</h2>
            <p style="font-style: italic; color: #666;">周易五行 · 黄历宜忌 · 仅供参考娱乐</p>
            
            <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 15px;">
                <div style="flex: 1; min-width: 150px; background: #f3e5f5; padding: 15px; border-radius: 8px;">
                    <p><strong>今日干支</strong></p>
                    <p style="font-size: 1.3em;">{{ metaphysics.ganzhi.day }}</p>
                    <p>日主: {{ metaphysics.day_element }}</p>
                </div>
                <div style="flex: 1; min-width: 150px; background: {{ '#e8f5e9' if metaphysics.fortune_score > 60 else '#ffebee' if metaphysics.fortune_score < 40 else '#fff8e1' }}; padding: 15px; border-radius: 8px;">
                    <p><strong>今日评分</strong></p>
                    <p style="font-size: 1.5em; color: {{ '#27ae60' if metaphysics.fortune_score > 60 else '#e74c3c' if metaphysics.fortune_score < 40 else '#f39c12' }};">
                        {{ metaphysics.fortune_score }}/100
                    </p>
                    <p>{{ metaphysics.fortune_desc }}</p>
                </div>
                <div style="flex: 1; min-width: 150px; background: #e3f2fd; padding: 15px; border-radius: 8px;">
                    <p><strong>宜</strong></p>
                    <p>{{ metaphysics.yi|join(', ') }}</p>
                </div>
                <div style="flex: 1; min-width: 150px; background: #fce4ec; padding: 15px; border-radius: 8px;">
                    <p><strong>忌</strong></p>
                    <p>{{ metaphysics.ji|join(', ') }}</p>
                </div>
            </div>
            
            <div style="margin-top: 15px;">
                <p><strong>有利行业:</strong> {{ metaphysics.favorable_sectors|join(', ') }}</p>
                <p><strong>不利行业:</strong> {{ metaphysics.unfavorable_sectors|join(', ') }}</p>
            </div>
            
            {% if metaphysics_stocks %}
            <h3 style="margin-top: 20px;">个股玄学评分</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f3e5f5;">
                        <th style="padding: 10px; text-align: left;">股票</th>
                        <th style="padding: 10px; text-align: center;">五行</th>
                        <th style="padding: 10px; text-align: center;">相性</th>
                        <th style="padding: 10px; text-align: center;">玄学评分</th>
                        <th style="padding: 10px; text-align: left;">建议</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in metaphysics_stocks %}
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px;">{{ stock.name }} ({{ stock.code }})</td>
                        <td style="padding: 10px; text-align: center;">{{ stock.stock_element }}</td>
                        <td style="padding: 10px; text-align: center;">{{ stock.compatibility.relationship }}</td>
                        <td style="padding: 10px; text-align: center;">
                            <span style="background: {{ '#27ae60' if stock.meta_score > 60 else '#e74c3c' if stock.meta_score < 40 else '#f39c12' }}; color: white; padding: 3px 8px; border-radius: 10px;">
                                {{ stock.meta_score }}
                            </span>
                        </td>
                        <td style="padding: 10px;">{{ stock.advice }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
            
            <p style="margin-top: 15px; font-size: 0.9em; color: #999;">
                * 玄学分析仅供文化参考，不构成投资建议。投资需基于基本面和技术分析。
            </p>
        </section>
        {% endif %}
        
        {% if expert_analysis %}
        <section class="section">
            <h2>投资大师策略分析</h2>
            <p>综合10位国内外投资大师的选股逻辑，多维度评估</p>
            
            <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px;">
                <div style="flex: 1; min-width: 200px; background: #e8f5e9; padding: 15px; border-radius: 8px;">
                    <h4>国际大师</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>巴菲特 - 价值投资</li>
                        <li>芒格 - 多元思维</li>
                        <li>彼得林奇 - 成长投资</li>
                        <li>格雷厄姆 - 安全边际</li>
                        <li>霍华德马克斯 - 周期</li>
                    </ul>
                </div>
                <div style="flex: 1; min-width: 200px; background: #e3f2fd; padding: 15px; border-radius: 8px;">
                    <h4>中国大师</h4>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>但斌 - 长期持有</li>
                        <li>林园 - 医药消费</li>
                        <li>段永平 - 商业模式</li>
                        <li>张磊 - 创新投资</li>
                        <li>邱国鹭 - 行业格局</li>
                    </ul>
                </div>
            </div>
            
            {% if expert_analysis.top_stocks %}
            <h3 style="margin-top: 20px;">大师共识推荐</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #667eea; color: white;">
                        <th style="padding: 10px; text-align: left;">股票</th>
                        <th style="padding: 10px; text-align: center;">大师评分</th>
                        <th style="padding: 10px; text-align: left;">核心观点</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in expert_analysis.top_stocks[:5] %}
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px;">{{ stock.name }} ({{ stock.code }})</td>
                        <td style="padding: 10px; text-align: center;">
                            <span style="background: {{ '#27ae60' if stock.total_score > 70 else '#f39c12' if stock.total_score > 50 else '#e74c3c' }}; color: white; padding: 3px 8px; border-radius: 10px;">
                                {{ "%.0f"|format(stock.total_score) }}
                            </span>
                        </td>
                        <td style="padding: 10px;">{{ stock.top_reason }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
        </section>
        {% endif %}
        
        {% if policy_recommendations %}
        <section class="section">
            <h2>政策导向分析</h2>
            <p>基于十四五规划和当前政策热点，分析政策红利方向</p>
            
            {% if policy_hotspots %}
            <h3 style="margin-top: 15px;">当前政策热点</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                {% for hotspot in policy_hotspots[:5] %}
                <span style="background: #ff9800; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.9em;">
                    {{ hotspot }}
                </span>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if policy_recommendations %}
            <h3 style="margin-top: 20px;">政策受益股</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #ff9800; color: white;">
                        <th style="padding: 10px; text-align: left;">股票</th>
                        <th style="padding: 10px; text-align: center;">政策评分</th>
                        <th style="padding: 10px; text-align: left;">相关政策</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in policy_recommendations[:5] %}
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px;">{{ stock.name }} ({{ stock.code }})</td>
                        <td style="padding: 10px; text-align: center;">
                            <span style="background: #ff9800; color: white; padding: 3px 8px; border-radius: 10px;">
                                {{ "%.0f"|format(stock.policy_score) }}
                            </span>
                        </td>
                        <td style="padding: 10px;">{{ stock.matched_areas|join(', ') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
        </section>
        {% endif %}
        
        {% if intl_overview %}
        <section class="section">
            <h2>国际形势分析</h2>
            <p>全球地缘政治和经济形势对A股的影响</p>
            
            <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px;">
                <div style="flex: 1; min-width: 200px; background: #e3f2fd; padding: 15px; border-radius: 8px;">
                    <h4>中美关系</h4>
                    <p>{{ intl_overview.us_china|default('持续博弈，科技竞争加剧') }}</p>
                </div>
                <div style="flex: 1; min-width: 200px; background: #fff3e0; padding: 15px; border-radius: 8px;">
                    <h4>全球经济</h4>
                    <p>{{ intl_overview.global_economy|default('美联储政策影响全球资金流向') }}</p>
                </div>
                <div style="flex: 1; min-width: 200px; background: #fce4ec; padding: 15px; border-radius: 8px;">
                    <h4>地缘风险</h4>
                    <p>{{ intl_overview.geopolitical|default('关注区域冲突对能源价格影响') }}</p>
                </div>
            </div>
            
            {% if intl_warnings %}
            <h3 style="margin-top: 20px;">风险提示</h3>
            <ul style="background: #fff3e0; padding: 15px 15px 15px 35px; border-radius: 8px;">
                {% for warning in intl_warnings[:5] %}
                <li style="margin-bottom: 5px;">{{ warning }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            
            {% if intl_recommendations %}
            <h3 style="margin-top: 20px;">国际形势受益股</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #1565c0; color: white;">
                        <th style="padding: 10px; text-align: left;">股票</th>
                        <th style="padding: 10px; text-align: center;">国际评分</th>
                        <th style="padding: 10px; text-align: left;">相关主题</th>
                    </tr>
                </thead>
                <tbody>
                    {% for stock in intl_recommendations[:5] %}
                    <tr style="border-bottom: 1px solid #eee;">
                        <td style="padding: 10px;">{{ stock.name }} ({{ stock.code }})</td>
                        <td style="padding: 10px; text-align: center;">
                            <span style="background: #1565c0; color: white; padding: 3px 8px; border-radius: 10px;">
                                {{ "%.0f"|format(stock.international_score) }}
                            </span>
                        </td>
                        <td style="padding: 10px;">{{ stock.beneficiary_events|join(', ') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
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
