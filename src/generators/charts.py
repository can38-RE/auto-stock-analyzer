"""Stock Chart Visualization Module.

Based on pyecharts for K-line charts and trend visualization.
Inspired by runoob.com Python-Qt tutorial.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger


class StockChartGenerator:
    """Generate stock charts using pyecharts."""
    
    def __init__(self, output_dir: str = "./reports/charts"):
        """Initialize chart generator.
        
        Args:
            output_dir: Directory to save chart HTML files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_kline_chart(self, stock_code: str, stock_name: str,
                              dates: List[str], ohlc_data: List[List[float]],
                              volume_data: List[float] = None) -> str:
        """Generate K-line (candlestick) chart.
        
        Args:
            stock_code: Stock code
            stock_name: Stock name
            dates: List of date strings
            ohlc_data: List of [open, close, low, high] lists
            volume_data: Optional volume data
            
        Returns:
            Path to generated HTML file
        """
        try:
            from pyecharts import options as opts
            from pyecharts.charts import Kline, Bar, Grid
            
            # Create K-line chart
            kline = (
                Kline()
                .add_xaxis(xaxis_data=dates)
                .add_yaxis(
                    series_name="K线",
                    y_axis=ohlc_data,
                    itemstyle_opts=opts.ItemStyleOpts(
                        color="#ef232a",  # Red for up
                        color0="#14b143",  # Green for down
                    ),
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(
                        title=f"{stock_name} ({stock_code}) K线图",
                        subtitle="数据来源: baostock"
                    ),
                    xaxis_opts=opts.AxisOpts(is_scale=True),
                    yaxis_opts=opts.AxisOpts(
                        is_scale=True,
                        splitarea_opts=opts.SplitAreaOpts(
                            is_show=True,
                            areastyle_opts=opts.AreaStyleOpts(opacity=1)
                        )
                    ),
                    datazoom_opts=[
                        opts.DataZoomOpts(pos_bottom="-2%", range_start=0, range_end=100, type_="inside"),
                        opts.DataZoomOpts(pos_bottom="-2%", range_start=0, range_end=100, type_="slider"),
                    ],
                    toolbox_opts=opts.ToolboxOpts(
                        feature={
                            "dataZoom": {"yAxisIndex": "none"},
                            "restore": {},
                            "saveAsImage": {},
                        }
                    ),
                    tooltip_opts=opts.TooltipOpts(
                        trigger="axis",
                        axis_pointer_type="cross"
                    ),
                )
            )
            
            # Save chart
            filename = f"kline_{stock_code}_{datetime.now().strftime('%Y%m%d')}.html"
            output_path = self.output_dir / filename
            kline.render(str(output_path))
            
            logger.info(f"K-line chart generated: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.warning("pyecharts not installed, skipping K-line chart")
            return ""
        except Exception as e:
            logger.error(f"Failed to generate K-line chart: {e}")
            return ""
    
    def generate_trend_chart(self, stock_code: str, stock_name: str,
                              dates: List[str], closes: List[float],
                              ma5: List[float] = None,
                              ma10: List[float] = None,
                              ma20: List[float] = None) -> str:
        """Generate stock trend line chart with moving averages.
        
        Args:
            stock_code: Stock code
            stock_name: Stock name
            dates: List of date strings
            closes: List of closing prices
            ma5: 5-day moving average
            ma10: 10-day moving average
            ma20: 20-day moving average
            
        Returns:
            Path to generated HTML file
        """
        try:
            from pyecharts import options as opts
            from pyecharts.charts import Line
            
            line = (
                Line()
                .add_xaxis(xaxis_data=dates)
                .add_yaxis(
                    series_name="收盘价",
                    y_axis=closes,
                    is_smooth=True,
                    linestyle_opts=opts.LineStyleOpts(width=2),
                    markpoint_opts=opts.MarkPointOpts(
                        data=[
                            opts.MarkPointItem(type_="max", name="最高价"),
                            opts.MarkPointItem(type_="min", name="最低价"),
                        ]
                    ),
                    markline_opts=opts.MarkLineOpts(
                        data=[opts.MarkLineItem(type_="average", name="平均值")]
                    ),
                )
            )
            
            # Add moving averages if provided
            if ma5:
                line.add_yaxis(
                    series_name="MA5",
                    y_axis=ma5,
                    is_smooth=True,
                    linestyle_opts=opts.LineStyleOpts(width=1, type_="dashed"),
                )
            
            if ma10:
                line.add_yaxis(
                    series_name="MA10",
                    y_axis=ma10,
                    is_smooth=True,
                    linestyle_opts=opts.LineStyleOpts(width=1, type_="dashed"),
                )
            
            if ma20:
                line.add_yaxis(
                    series_name="MA20",
                    y_axis=ma20,
                    is_smooth=True,
                    linestyle_opts=opts.LineStyleOpts(width=1, type_="dashed"),
                )
            
            line.set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"{stock_name} ({stock_code}) 走势图",
                    subtitle="含均线分析"
                ),
                xaxis_opts=opts.AxisOpts(type_="category"),
                yaxis_opts=opts.AxisOpts(is_scale=True),
                datazoom_opts=[
                    opts.DataZoomOpts(pos_bottom="-2%", range_start=0, range_end=100, type_="inside"),
                    opts.DataZoomOpts(pos_bottom="-2%", range_start=0, range_end=100, type_="slider"),
                ],
                toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "dataZoom": {"yAxisIndex": "none"},
                        "restore": {},
                        "saveAsImage": {},
                    }
                ),
            )
            
            # Save chart
            filename = f"trend_{stock_code}_{datetime.now().strftime('%Y%m%d')}.html"
            output_path = self.output_dir / filename
            line.render(str(output_path))
            
            logger.info(f"Trend chart generated: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.warning("pyecharts not installed, skipping trend chart")
            return ""
        except Exception as e:
            logger.error(f"Failed to generate trend chart: {e}")
            return ""
    
    def generate_sector_heatmap(self, sectors: List[Dict[str, Any]]) -> str:
        """Generate sector performance heatmap.
        
        Args:
            sectors: List of sector data with name and performance
            
        Returns:
            Path to generated HTML file
        """
        try:
            from pyecharts import options as opts
            from pyecharts.charts import Bar
            
            sector_names = [s.get('name', '') for s in sectors]
            changes = [s.get('change', 0) for s in sectors]
            
            colors = ['#e74c3c' if c > 0 else '#27ae60' for c in changes]
            
            bar = (
                Bar()
                .add_xaxis(xaxis_data=sector_names)
                .add_yaxis(
                    series_name="涨跌幅",
                    y_axis=changes,
                    itemstyle_opts=opts.ItemStyleOpts(color="#667eea"),
                )
                .set_global_opts(
                    title_opts=opts.TitleOpts(title="板块涨跌幅排行"),
                    xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
                    yaxis_opts=opts.AxisOpts(is_scale=True),
                )
            )
            
            filename = f"sector_heatmap_{datetime.now().strftime('%Y%m%d')}.html"
            output_path = self.output_dir / filename
            bar.render(str(output_path))
            
            logger.info(f"Sector heatmap generated: {output_path}")
            return str(output_path)
            
        except ImportError:
            logger.warning("pyecharts not installed, skipping sector heatmap")
            return ""
        except Exception as e:
            logger.error(f"Failed to generate sector heatmap: {e}")
            return ""


def generate_stock_charts_for_report(analysis_results: Dict[str, Any]) -> Dict[str, str]:
    """Generate charts for the analysis report.
    
    Args:
        analysis_results: Analysis results dictionary
        
    Returns:
        Dictionary of chart paths
    """
    chart_gen = StockChartGenerator()
    charts = {}
    
    # Generate charts for top stocks
    trend_analysis = analysis_results.get('trend_analysis', [])
    
    for stock in trend_analysis[:5]:
        try:
            code = stock.get('code', '')
            name = stock.get('name', '')
            
            # Get recent prices
            recent_prices = stock.get('recent_prices', [])
            if not recent_prices:
                continue
            
            dates = [p.get('date', '') for p in recent_prices]
            closes = [p.get('close', 0) for p in recent_prices]
            opens = [p.get('open', 0) for p in recent_prices]
            highs = [p.get('high', 0) for p in recent_prices]
            lows = [p.get('low', 0) for p in recent_prices]
            
            # Prepare OHLC data for K-line
            ohlc_data = [[o, c, l, h] for o, c, l, h in zip(opens, closes, lows, highs)]
            
            # Generate K-line chart
            kline_path = chart_gen.generate_kline_chart(code, name, dates, ohlc_data)
            if kline_path:
                charts[f"kline_{code}"] = kline_path
            
            # Generate trend chart
            trend_path = chart_gen.generate_trend_chart(code, name, dates, closes)
            if trend_path:
                charts[f"trend_{code}"] = trend_path
            
        except Exception as e:
            logger.warning(f"Failed to generate charts for {stock.get('code')}: {e}")
    
    # Generate sector heatmap
    sector_analysis = analysis_results.get('sector_analysis', {})
    top_sectors = sector_analysis.get('top_sectors', {})
    
    if top_sectors:
        sectors = []
        for name, data in top_sectors.items():
            sectors.append({
                'name': name,
                'change': data.get('avg_change', 0)
            })
        
        heatmap_path = chart_gen.generate_sector_heatmap(sectors)
        if heatmap_path:
            charts['sector_heatmap'] = heatmap_path
    
    return charts
