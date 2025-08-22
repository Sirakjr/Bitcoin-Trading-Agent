import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import json
import pandas as pd

from src.config.config_manager import load_config


def calculate_weekly_metrics():
	"""Calculate P&L and trade metrics for the last 7 days."""
	trades_file = Path("data/trades.csv")
	if not trades_file.exists():
		return {"error": "No trades data found"}

	# Read trades and filter last 7 days
	df = pd.read_csv(trades_file)
	df['timestamp'] = pd.to_datetime(df['timestamp'])
	week_ago = datetime.now() - timedelta(days=7)
	weekly_trades = df[df['timestamp'] >= week_ago]

	if weekly_trades.empty:
		return {"error": "No trades in last 7 days"}

	# Calculate metrics
	total_trades = len(weekly_trades)
	dca_trades = len(weekly_trades[weekly_trades['notes'] == 'DCA'])
	swing_trades = len(weekly_trades[weekly_trades['notes'].str.contains('swing', case=False, na=False)])

	# Simple P&L calculation (approximate)
	portfolio_file = Path("data/portfolio.json")
	if portfolio_file.exists():
		with portfolio_file.open("r") as f:
			portfolio = json.load(f)
		current_btc = float(portfolio.get("btc", 0))
		current_cash = float(portfolio.get("cash_usd", 0))
	else:
		current_btc = 0
		current_cash = 0

	# Get current BTC price for valuation
	try:
		from src.data.price_data import get_latest_price_and_atr
		market = get_latest_price_and_atr()
		current_price = float(market.get("price", 0))
	except Exception:
		current_price = 0

	current_value = current_btc * current_price + current_cash
	
	# Calculate weekly change (simplified)
	weekly_pnl = 0  # Would need historical portfolio values for accurate P&L
	weekly_pnl_pct = 0

	return {
		"total_trades": total_trades,
		"dca_trades": dca_trades,
		"swing_trades": swing_trades,
		"current_btc": current_btc,
		"current_value": current_value,
		"weekly_pnl": weekly_pnl,
		"weekly_pnl_pct": weekly_pnl_pct,
		"current_price": current_price
	}


def generate_weekly_report():
	"""Generate weekly report content."""
	metrics = calculate_weekly_metrics()
	
	if "error" in metrics:
		return f"Weekly Report Error: {metrics['error']}"

	# Get ML insights if available
	overrides_file = Path("src/ml/runtime_overrides.json")
	ml_insight = ""
	if overrides_file.exists():
		try:
			with overrides_file.open("r") as f:
				overrides = json.load(f)
			if overrides.get("pred_return"):
				ml_insight = f"ML Forecast: {overrides['pred_return']:.3f} return, Strength: {overrides.get('pred_strength', 0):.2f}"
		except Exception:
			pass

	report = f"""
Bitcoin Trading Agent - Weekly Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Portfolio Summary:
- Total BTC: {metrics['current_btc']:.6f}
- Current Value: ${metrics['current_value']:,.2f}
- BTC Price: ${metrics['current_price']:,.2f}

Weekly Activity:
- Total Trades: {metrics['total_trades']}
- DCA Trades: {metrics['dca_trades']}
- Swing Trades: {metrics['swing_trades']}

ML Insights:
{ml_insight if ml_insight else "No ML insights available"}

Note: This is a paper trading system. All trades are simulated.
	"""
	return report.strip()


def send_weekly_report():
	"""Send weekly report via Gmail."""
	cfg = load_config()
	
	# Check if email is enabled
	if not cfg.get("GMAIL_USER") or not cfg.get("GMAIL_APP_PASSWORD"):
		print("Gmail credentials not configured")
		return False

	try:
		# Create message
		msg = MIMEMultipart()
		msg['From'] = cfg["GMAIL_USER"]
		msg['To'] = cfg["GMAIL_USER"]  # Send to self for now
		msg['Subject'] = f"Bitcoin Trading Agent - Weekly Report {datetime.now().strftime('%Y-%m-%d')}"

		# Generate report content
		report_content = generate_weekly_report()
		msg.attach(MIMEText(report_content, 'plain'))

		# Send email
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(cfg["GMAIL_USER"], cfg["GMAIL_APP_PASSWORD"])
		server.send_message(msg)
		server.quit()

		print("Weekly report sent successfully")
		return True

	except Exception as e:
		print(f"Failed to send weekly report: {e}")
		return False


if __name__ == "__main__":
	# Test report generation
	print(generate_weekly_report())
