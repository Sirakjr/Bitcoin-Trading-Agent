# Bitcoin Trading Agent

A smart, ML-enhanced Bitcoin trading system that combines Dollar-Cost Averaging (DCA) with adaptive swing trading using ARIMA forecasting and ATR-based risk management.

## 🎯 Project Overview

This system operates with minimal human supervision, continuously adapting to market conditions through:
- **DCA Base Layer**: Accumulates Bitcoin on price drops with configurable thresholds
- **ML-Enhanced Swing Trading**: Uses ARIMA(1,1,2) forecasting to enable/disable swing trades
- **Dynamic Risk Management**: ATR-based stops and portfolio-level drawdown protection
- **24/7 Operation**: Automated trading with Telegram alerts and weekly email reports

## 🏗️ Architecture

```
src/
├── config/           # Configuration management (Google Sheets + local cache)
├── data/            # Price data fetching (Coinbase API)
├── strategy/        # DCA + Hybrid strategy logic
├── broker/          # Paper trading execution
├── ml/              # ARIMA forecasting + threshold adaptation
├── notify/          # Telegram + Gmail notifications
├── backtest/        # Strategy validation engine
├── scheduler.py     # 24/7 job orchestration
└── main.py          # Main trading loop
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file with:
```env
# Trading Configuration
BUDGET_USD=10000
DCA_AMOUNT_USD=500
DCA_DROP_PERCENT=3.0
MAX_DRAWDOWN_PCT=25.0
TRADING_MODE=hybrid

# Google Sheets (optional)
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON_PATH=path/to/service_account.json

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Gmail (optional)
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

### 3. Run the System

**Single Trading Cycle:**
```bash
python -m src.main
```

**Continuous 24/7 Operation:**
```bash
python -m src.scheduler
```

## 🐳 Docker Deployment

### Local Development
```bash
# 1. Copy environment file
cp env.example .env

# 2. Edit configuration
nano .env

# 3. Build and run
docker-compose up -d

# 4. View logs
docker-compose logs -f bitcoin-trading-agent
```

### Production Deployment
```bash
# Build and deploy
./deploy.sh

# Or manually
docker build -t bitcoin-trading-agent .
docker run -d --name bitcoin-trading-agent --restart unless-stopped --env-file .env -v "$(pwd)/data:/app/data" bitcoin-trading-agent
```

**For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)**

## 📊 How It Works

### Trading Logic
1. **DCA Strategy**: Buys $500 when BTC drops 3% (configurable)
2. **ML Adaptation**: ARIMA forecasts adjust thresholds hourly
3. **Swing Trading**: Opens tactical positions when forecast is positive
4. **Risk Management**: ATR-based stops + portfolio drawdown protection

### ML Enhancement
- **Forecasting**: ARIMA(1,1,2) predicts next price movement
- **Threshold Adaptation**: Maps forecasts to runtime overrides
- **Dynamic Behavior**: Enables/disables swing trades based on market conditions

### Risk Controls
- **ATR Stops**: Stop = Entry - k × ATR (k adapted by ML)
- **Portfolio Guard**: Pauses all trading if drawdown > 25%
- **Position Limits**: One swing trade at a time

## 🔧 Configuration

### Trading Modes
- **`TRADING_MODE=dca_only`**: Pure DCA strategy, no swing trading
- **`TRADING_MODE=hybrid`**: DCA + swing trading (default)

### Google Sheets Integration
- Store trading parameters in Google Sheets
- Hourly refresh with local JSON fallback
- Secure service account authentication

### Dynamic Parameters
- `dca_drop_percent`: DCA trigger threshold
- `atr_k_stop`: ATR multiplier for stops
- `enable_swing`: ML-driven swing trade enable/disable

## 📈 Monitoring & Reporting

### Real-time Alerts
- **Telegram**: Instant notifications for all trades
- **Console**: Detailed logging of decisions and executions

### Weekly Reports
- **Email**: Monday 9:00 AM Gmail summary
- **Metrics**: Portfolio value, trade counts, ML insights
- **Performance**: Weekly P&L and activity summary

## 📊 Backtesting

### Strategy Validation
```bash
python -m src.backtest.engine
```

### Output
- Historical performance simulation
- Trade-by-trade analysis
- Risk metrics (max drawdown, returns)
- Results saved to `data/backtest/`

### Mode Comparison
Test different trading modes:
```python
# DCA only
engine = BacktestEngine(trading_mode="dca_only")

# Hybrid mode
engine = BacktestEngine(trading_mode="hybrid")
```

## 🚨 Risk Management

### Portfolio Protection
- **Drawdown Limit**: Configurable maximum loss threshold
- **Risk Pause**: Automatic trading suspension on breach
- **Recovery**: Resumes trading when portfolio recovers

### Trade-Level Controls
- **ATR Stops**: Volatility-adjusted stop losses
- **Position Sizing**: Fixed USD amounts per trade
- **Trade Limits**: Maximum one swing position

## 🔄 System Operation

### Scheduler Jobs
- **Every 30 minutes**: Execute trading cycle
- **Every hour**: Update ML overrides
- **Monday 9:00 AM**: Send weekly email report

### Data Flow
1. Fetch latest BTC price + ATR
2. Run ARIMA forecast
3. Adapt thresholds based on forecast
4. Evaluate DCA + swing opportunities
5. Execute trades via paper broker
6. Send Telegram notifications
7. Persist portfolio state

## 📁 Data Storage

### Trade Records
- `data/trades.csv`: All executed trades
- `data/portfolio.json`: Current portfolio state
- `data/active_trades.json`: Open swing positions

### ML State
- `src/ml/runtime_overrides.json`: Current ML adaptations
- `data/backtest/`: Historical validation results

## 🛠️ Development

### Adding New Features
- **Strategies**: Extend `StrategyManager` class
- **Indicators**: Add to `src/features/` directory
- **Brokers**: Implement new broker classes

### Testing
- **Unit Tests**: Individual component validation
- **Backtesting**: Historical strategy validation
- **Paper Trading**: Live simulation without risk

## 📋 Requirements

- Python 3.8+
- Key dependencies: pandas, numpy, statsmodels, requests
- Optional: Google Sheets API, Telegram Bot API, Gmail SMTP
- **Docker** (for containerized deployment)

## ⚠️ Disclaimer

This is a **paper trading system** for educational purposes. All trades are simulated and no real money is at risk. The system demonstrates algorithmic trading concepts and should not be used for actual investment decisions without proper validation and risk assessment.

## 📞 Support

For questions or issues:
1. Check the configuration and environment setup
2. Review console logs for error messages
3. Validate data sources and API connections
4. Test individual components in isolation
5. Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues

---

**Status**: MVP Complete - Core trading logic, ML adaptation, risk management, monitoring, trading mode toggle, and Docker deployment ready. Ready for production deployment! 🚀