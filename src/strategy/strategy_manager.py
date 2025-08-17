from datetime import datetime

from src.strategy.dca_strategy import DCAStrategy


class StrategyManager:
	"""Minimal orchestrator for DCA-first paper trading.

	Extensible later to include ATR swing and guardrails.
	"""

	def __init__(
		self,
		budget_usd: float,
		dca_amount_usd: float,
		dca_drop_percent: float,
		min_interval_hours: int = 24,
	):
		self.dca = DCAStrategy(
			budget_usd=budget_usd,
			dca_amount_usd=dca_amount_usd,
			drop_percent=dca_drop_percent,
			min_interval_hours=min_interval_hours,
		)
		self._last_close_price = None

	def step(self, current_price, now=None):
		"""Given current price, decide whether to DCA buy.

		Returns a dict with an action description.
		"""
		now = now or datetime.now()
		previous_price = self._last_close_price if self._last_close_price is not None else current_price
		decision = self.dca.should_buy(current_price, previous_price, now)
		self._last_close_price = current_price
		return {"action": "buy" if decision.get("should_buy") else "hold", **decision}


