# AutoStockAnalyzer

全自动A股分析智能模型 - 每日自动分析市场并生成调仓策略

## 功能特性

- 📊 全市场扫描：自动扫描全部A股（约5000只）
- 📰 多源新闻聚合：爬取新浪财经、东方财富、同花顺等财经新闻
- 🔥 社会热点追踪：监控微博、知乎、百度热搜
- 📈 板块轮动分析：识别行业轮动趋势
- 🤖 AI智能分析：使用MiMo模型进行深度分析
- 📋 策略生成：针对1000元本金生成调仓建议
- 📄 HTML报告：生成美观的可视化分析报告
- ⏰ 自动调度：通过GitHub Actions每天8点自动执行

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/auto-stock-analyzer.git
cd auto-stock-analyzer
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
MIMO_API_KEY=your_api_key_here
```

### 4. 运行分析

```bash
python -m src.main
```

## 项目结构

```
auto-stock-analyzer/
├── src/
│   ├── collectors/          # 数据采集模块
│   ├── analyzers/           # 分析模块
│   ├── generators/          # 报告生成模块
│   ├── scheduler/           # 调度模块
│   └── config/              # 配置管理
├── config/
│   └── config.yaml          # 主配置文件
├── reports/                 # 生成的报告
├── data/                    # 数据缓存
├── tests/                   # 单元测试
├── .github/
│   └── workflows/
│       └── daily_analysis.yml # GitHub Actions工作流
├── requirements.txt         # Python依赖
└── README.md                # 项目说明
```

## 配置说明

编辑 `config/config.yaml` 文件：

```yaml
# 资金配置
capital:
  initial: 1000
  currency: "CNY"

# 风险管理
risk:
  level: "dynamic"
  max_position: 0.2
  stop_loss: 0.08
```

## 部署到GitHub

1. Fork本项目到你的GitHub账户
2. 在Settings → Secrets中添加 `MIMO_API_KEY`
3. 启用GitHub Pages
4. 等待每天8点自动执行

## 报告示例

生成的报告包含：
- 市场概览（大盘指数）
- 市场情绪分析
- 风险评估
- 新闻分析
- 板块分析
- 股票推荐
- 投资组合建议

## 声明

⚠️ **风险提示**：
- 本系统仅用于学习和研究目的
- 不构成任何投资建议
- 股市有风险，投资需谨慎
- 使用本系统产生的任何投资决策及其后果，由用户自行承担

## License

MIT License
