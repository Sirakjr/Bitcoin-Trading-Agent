from datetime import datetime

from src.config.config_manager import load_config
from src.data.price_data import get_latest_price_and_atr
from src.strategy.strategy_manager import StrategyManager
from src.broker.paper_broker import set_initial_cash, get_position, place_market_buy
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
	)

	decision = manager.step(current_price=price, now=datetime.now())
	if decision.get("should_buy"):
		filled = place_market_buy(price_usd=price, amount_usd=float(decision["amount_usd"]))
		pos = get_position()
		msg = (
			f"DCA Buy: ${filled['amount_usd']:.2f} at ${filled['price_usd']:.2f}. "
			f"BTC +{filled['btc_amount']:.6f}. Portfolio: {pos['btc']:.6f} BTC, ${pos['cash_usd']:.2f} cash."
		)
		print(msg)
		send_message(msg)
	else:
		print(f"Hold: {decision.get('reason')}")


if __name__ == "__main__":
	run_once()


