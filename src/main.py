from datetime import datetime

from src.config.config_manager import load_config
from src.data.price_data import get_latest_price_and_atr
from src.strategy.strategy_manager import StrategyManager
from src.broker.paper_broker import set_initial_cash, get_position, place_market_buy, place_market_sell
from src.notify.telegram import send_message
from src.ml.threshold_adapter import read_overrides


def run_once():
	cfg = load_config()
	market = get_latest_price_and_atr()
	if "error" in market:
		print(market["error"]) 
		return
	
	price = float(market["price"])  # latest close
	print(f"Price now: ${price:,.2f}")

	# Initialize paper broker cash once (idempotent for dev: resets cash each run)
	set_initial_cash(float(cfg.get("BUDGET_USD", 10000)))

	manager = StrategyManager(
		budget_usd=float(cfg.get("BUDGET_USD", 10000)),
		dca_amount_usd=float(cfg.get("DCA_AMOUNT_USD", 500)),
		dca_drop_percent=float(read_overrides().get("dca_drop_percent", cfg.get("DCA_DROP_PERCENT", 3.0))),
		min_interval_hours=int(cfg.get("DCA_MIN_INTERVAL_HOURS", 24)),
		max_drawdown_pct=float(cfg.get("MAX_DRAWDOWN_PCT", 25.0)),
		trading_mode=cfg.get("TRADING_MODE", "hybrid"),
	)

	overrides = read_overrides()
	market_atr = float(market.get("atr", 0.0))
	hybrid = manager.evaluate_hybrid(
		current_price=price,
		atr_value=market_atr,
		now=datetime.now(),
		overrides=overrides,
		swing_amount_usd=float(cfg.get("SWING_AMOUNT_USD", cfg.get("DCA_AMOUNT_USD", 500))),
	)

	# Check if risk pause is active
	if hybrid.get("risk_pause"):
		print(f"🚨 RISK PAUSE: {hybrid.get('risk_message')}")
		return

	# DCA action
	if hybrid["dca"].get("should_buy"):
		filled = place_market_buy(price_usd=price, amount_usd=float(hybrid["dca"]["amount_usd"]))
		pos = get_position()
		msg = (
			f"DCA Buy: ${filled['amount_usd']:.2f} at ${filled['price_usd']:.2f}. "
			f"BTC +{filled['btc_amount']:.6f}. Portfolio: {pos['btc']:.6f} BTC, ${pos['cash_usd']:.2f} cash."
		)
		print(msg)
		send_message(msg)
	else:
		print(f"DCA Hold: {hybrid['dca'].get('reason')}")

	# Swing open (only if hybrid mode and enabled)
	if hybrid.get("swing_open"):
		tr = hybrid["swing_open"]
		# Execute buy
		filled = place_market_buy(price_usd=price, amount_usd=float(tr["amount_usd"]))
		manager.record_swing_open({**tr, **filled})
		pos = get_position()
		msg = (
			f"Swing Open: ${filled['amount_usd']:.2f} at ${filled['price_usd']:.2f}, "
			f"Stop ${tr['stop_loss']:.2f} (k={tr['atr_k']:.2f}). Portfolio: {pos['btc']:.6f} BTC."
		)
		print(msg)
		send_message(msg)

	# Swing stop closures
	for tr in hybrid.get("swing_closures", []):
		btc = float(tr.get("btc_amount", 0))
		if btc > 0:
			filled = place_market_sell(price_usd=price, btc_amount=btc)
			manager.record_swing_close(tr.get("trade_id"))
			msg = (
				f"Swing Stop Hit: Sold {btc:.6f} BTC at ${price:.2f}. "
				f"Entry ${tr['entry_price']:.2f}, Stop ${tr['stop_loss']:.2f}."
			)
			print(msg)
			send_message(msg)


if __name__ == "__main__":
	run_once()


