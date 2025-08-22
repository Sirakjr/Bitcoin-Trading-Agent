import json
from datetime import datetime
from pathlib import Path
import pandas as pd

from src.strategy.strategy_manager import StrategyManager
from src.ml.threshold_adapter import read_overrides


class BacktestEngine:
	"""Simple backtesting engine using StrategyManager."""
	
	def __init__(self, initial_budget=10000, max_drawdown_pct=25.0, trading_mode="hybrid"):
		self.initial_budget = float(initial_budget)
		self.max_drawdown_pct = float(max_drawdown_pct)
		self.trading_mode = trading_mode
		self.trades = []
		self.portfolio_history = []
		
	def run_backtest(self, historical_data, dca_config, overrides=None):
		"""Run backtest on historical data."""
		if historical_data.empty:
			return {"error": "No historical data provided"}
		
		# Initialize strategy manager
		manager = StrategyManager(
			budget_usd=self.initial_budget,
			dca_amount_usd=float(dca_config.get("dca_amount_usd", 500)),
			dca_drop_percent=float(dca_config.get("dca_drop_percent", 3.0)),
			min_interval_hours=int(dca_config.get("min_interval_hours", 24)),
			max_drawdown_pct=self.max_drawdown_pct,
			trading_mode=self.trading_mode
		)
		
		# Initialize portfolio
		cash = self.initial_budget
		btc = 0.0
		overrides = overrides or {}
		
		# Process each historical bar
		for i, row in historical_data.iterrows():
			price = float(row['Close'])
			timestamp = pd.to_datetime(row.name)
			
			# Get ATR if available
			atr_value = float(row.get('ATR', 0)) if 'ATR' in row else 0
			
			# Evaluate strategy
			hybrid = manager.evaluate_hybrid(
				current_price=price,
				atr_value=atr_value,
				now=timestamp,
				overrides=overrides,
				swing_amount_usd=float(dca_config.get("dca_amount_usd", 500))
			)
			
			# Record portfolio state
			portfolio_value = cash + (btc * price)
			drawdown_pct = ((self.initial_budget - portfolio_value) / self.initial_budget) * 100
			
			self.portfolio_history.append({
				"timestamp": timestamp.isoformat(),
				"price": price,
				"cash": cash,
				"btc": btc,
				"portfolio_value": portfolio_value,
				"drawdown_pct": drawdown_pct,
				"risk_pause": hybrid.get("risk_pause", False)
			})
			
			# Execute DCA if allowed
			if not hybrid.get("risk_pause") and hybrid["dca"].get("should_buy"):
				amount = float(hybrid["dca"]["amount_usd"])
				if cash >= amount:
					btc_amount = amount / price
					cash -= amount
					btc += btc_amount
					
					self.trades.append({
						"timestamp": timestamp.isoformat(),
						"type": "DCA",
						"price": price,
						"amount_usd": amount,
						"btc_amount": btc_amount
					})
			
			# Execute swing if allowed (only in hybrid mode)
			if self.trading_mode == "hybrid" and not hybrid.get("risk_pause") and hybrid.get("swing_open"):
				tr = hybrid["swing_open"]
				amount = float(tr["amount_usd"])
				if cash >= amount:
					btc_amount = amount / price
					cash -= amount
					btc += btc_amount
					
					self.trades.append({
						"timestamp": timestamp.isoformat(),
						"type": "SWING",
						"price": price,
						"amount_usd": amount,
						"btc_amount": btc_amount,
						"stop_loss": tr["stop_loss"]
					})
			
			# Check swing stops
			for tr in hybrid.get("swing_closures", []):
				btc_to_sell = float(tr.get("btc_amount", 0))
				if btc_to_sell > 0 and btc >= btc_to_sell:
					btc -= btc_to_sell
					cash += btc_to_sell * price
					
					self.trades.append({
						"timestamp": timestamp.isoformat(),
						"type": "STOP",
						"price": price,
						"amount_usd": btc_to_sell * price,
						"btc_amount": btc_to_sell
					})
		
		# Final portfolio state
		final_price = float(historical_data['Close'].iloc[-1])
		final_value = cash + (btc * final_price)
		total_return = ((final_value - self.initial_budget) / self.initial_budget) * 100
		
		return {
			"initial_budget": self.initial_budget,
			"final_value": final_value,
			"total_return_pct": total_return,
			"total_trades": len(self.trades),
			"dca_trades": len([t for t in self.trades if t["type"] == "DCA"]),
			"swing_trades": len([t for t in self.trades if t["type"] == "SWING"]),
			"stop_trades": len([t for t in self.trades if t["type"] == "STOP"]),
			"final_cash": cash,
			"final_btc": btc,
			"max_drawdown": max([p["drawdown_pct"] for p in self.portfolio_history]) if self.portfolio_history else 0,
			"trading_mode": self.trading_mode
		}
	
	def save_results(self, output_dir="data/backtest"):
		"""Save backtest results to files."""
		Path(output_dir).mkdir(parents=True, exist_ok=True)
		
		# Save trades
		trades_file = Path(output_dir) / "trades.json"
		with trades_file.open("w", encoding="utf-8") as f:
			json.dump(self.trades, f, indent=2, default=str)
		
		# Save portfolio history
		portfolio_file = Path(output_dir) / "portfolio_history.json"
		with portfolio_file.open("w", encoding="utf-8") as f:
			json.dump(self.portfolio_history, f, indent=2, default=str)
		
		print(f"Backtest results saved to {output_dir}")


def run_simple_backtest():
	"""Run a simple backtest using available data."""
	try:
		from src.data.price_data import fetch_bitcoin_data
		from src.ml.threshold_adapter import read_overrides
		
		# Fetch historical data
		df = fetch_bitcoin_data()
		if df.empty:
			print("No historical data available for backtest")
			return
		
		# Calculate ATR for the data
		from src.data.price_data import calculate_atr
		df['ATR'] = calculate_atr(df)
		
		# Get current overrides
		overrides = read_overrides()
		
		# Run backtest in hybrid mode (default)
		engine = BacktestEngine(initial_budget=10000, max_drawdown_pct=25.0, trading_mode="hybrid")
		results = engine.run_backtest(
			historical_data=df,
			dca_config={
				"dca_amount_usd": 500,
				"dca_drop_percent": 3.0,
				"min_interval_hours": 24
			},
			overrides=overrides
		)
		
		print("Backtest Results:")
		print(json.dumps(results, indent=2))
		
		# Save results
		engine.save_results()
		
	except Exception as e:
		print(f"Backtest failed: {e}")


if __name__ == "__main__":
	run_simple_backtest()
