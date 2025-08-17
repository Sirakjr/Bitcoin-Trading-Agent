import json
from pathlib import Path


RUNTIME_OVERRIDES = Path("src/ml/runtime_overrides.json")


def _clamp(value, lo, hi):
	return max(lo, min(hi, value))


def adapt_thresholds(base_cfg, pred_return, pred_strength, atr_value):
	"""Map forecast to simple runtime overrides for hybrid mode.

	- Tighten ATR k slightly if positive expectation; loosen if negative.
	- Nudge DCA drop percent inversely to expectation.
	"""
	base_k = float(base_cfg.get("ATR_MULTIPLIER", 1.5))
	base_drop = float(base_cfg.get("DCA_DROP_PERCENT", 3.0))

	# Example mapping: +/- 0.5 on k within [1.0, 2.5]
	k = base_k - pred_return * 5.0  # +ret → smaller k (tighter); -ret → larger k
	k = _clamp(k, 1.0, 2.5)

	# Nudge DCA drop by up to +/- 1.0pp based on expectation
	drop = base_drop + (-pred_return * 100.0) * 0.3
	drop = _clamp(drop, 1.0, 8.0)

	enable_swing = pred_return > 0 and pred_strength > 0.2

	return {
		"enable_swing": bool(enable_swing),
		"atr_k_stop": round(k, 2),
		"dca_drop_percent": round(drop, 2),
	}


def write_overrides(payload):
	RUNTIME_OVERRIDES.parent.mkdir(parents=True, exist_ok=True)
	with RUNTIME_OVERRIDES.open("w", encoding="utf-8") as f:
		json.dump(payload, f, indent=2)


def read_overrides():
	if not RUNTIME_OVERRIDES.exists():
		return {}
	try:
		with RUNTIME_OVERRIDES.open("r", encoding="utf-8") as f:
			return json.load(f)
	except Exception:
		return {}


