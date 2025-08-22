import json
import warnings
from pathlib import Path

import numpy as np

from src.data.price_data import fetch_bitcoin_data
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.ar_model import AutoReg
from statsmodels.tsa.arima.model import ARIMA


def _mae(preds, actuals):
	mask = ~np.isnan(preds)
	if not mask.any():
		return float("nan")
	return float(np.mean(np.abs(preds[mask] - actuals[mask])))



def _walk_forward(close, train_len, test_len, fit_fn):
	y = close.astype(float).dropna()
	if len(y) < train_len + test_len:
		return float("nan"), 0
	start = len(y) - test_len
	preds = []
	actuals = []
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		for i in range(start, len(y)):
			train = y[i - train_len:i]
			actuals.append(float(y.iloc[i]))
			try:
				pred = fit_fn(train)
			except Exception:
				pred = np.nan
			preds.append(pred)
	actuals = np.array(actuals, dtype=float)
	preds = np.array(preds, dtype=float)
	return _mae(preds, actuals), int(np.sum(~np.isnan(preds)))


def grid_search_cv(close, train_len=60, test_len=14):
	results = {"ES": {}, "AR": {}, "ARIMA": {}}

	# ES(add) with/without damping
	for damped in (False, True):
		def fit_es(train, _damped=damped):
			m = ExponentialSmoothing(train, trend="add", seasonal=None, damped_trend=_damped).fit(optimized=True)
			return float(m.forecast(1).iloc[0])
		mae, n = _walk_forward(close, train_len, test_len, fit_es)
		results["ES"][f"add_damped={damped}"] = {"MAE": mae, "n": n}

	# AR with different lags
	for lags in (3, 5, 7, 10):
		def fit_ar(train, _lags=lags):
			m = AutoReg(train, lags=_lags, old_names=False).fit()
			return float(m.forecast(1).iloc[0])
		mae, n = _walk_forward(close, train_len, test_len, fit_ar)
		results["AR"][f"lags={lags}"] = {"MAE": mae, "n": n}

	# ARIMA grid (tiny)
	for p in (0, 1, 2):
		for q in (0, 1, 2):
			def fit_arima(train, _p=p, _q=q):
				m = ARIMA(train, order=(_p, 1, _q)).fit()
				return float(m.forecast(1).iloc[0])
			mae, n = _walk_forward(close, train_len, test_len, fit_arima)
			results["ARIMA"][f"({p},1,{q})"] = {"MAE": mae, "n": n}

	# Pick best per family
	summary = {"details": results, "best": {}}
	for family, cfgs in results.items():
		best_cfg = None
		best_mae = float("inf")
		for name, val in cfgs.items():
			mae = val["MAE"]
			if mae == mae and mae < best_mae:  # check not NaN and better
				best_mae = mae
				best_cfg = name
		summary["best"][family] = {"config": best_cfg, "MAE": best_mae}
	return summary


def main():
	df = fetch_bitcoin_data(period="60d")
	if df.empty or "Close" not in df.columns:
		print("No data available for grid search.")
		return
	res = grid_search_cv(df["Close"], train_len=20, test_len=7)
	print("Grid search summary:")
	print(json.dumps(res["best"], indent=2))
	Path("data").mkdir(parents=True, exist_ok=True)
	with Path("data/grid_search_cv_results.json").open("w", encoding="utf-8") as f:
		json.dump(res, f, indent=2)


if __name__ == "__main__":
	main()


