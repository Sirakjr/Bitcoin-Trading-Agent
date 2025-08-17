from __future__ import annotations

import warnings
import numpy as np
import pandas as pd

try:
	from statsmodels.tsa.holtwinters import ExponentialSmoothing
except Exception:  # pragma: no cover
	ExponentialSmoothing = None  # type: ignore

try:
	from statsmodels.tsa.ar_model import AutoReg
except Exception:  # pragma: no cover
	AutoReg = None  # type: ignore

try:
	from statsmodels.tsa.arima.model import ARIMA
except Exception:  # pragma: no cover
	ARIMA = None  # type: ignore


def forecast_next(candles_df: pd.DataFrame):
	"""Forecast next close using a tiny ensemble: ES(add), AR, ARIMA.

	Returns (pred_return, pred_strength) where pred_return is fractional return.
	Falls back to neutral (0, 0) if not enough data or all models fail.
	"""
	try:
		if candles_df is None or candles_df.empty or "Close" not in candles_df.columns:
			return 0.0, 0.0
		series = candles_df["Close"].astype(float).tail(300)
		if len(series) < 20:
			return 0.0, 0.0

		preds = []
		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			# ES additive trend
			if ExponentialSmoothing is not None:
				try:
					m = ExponentialSmoothing(series, trend="add", seasonal=None).fit(optimized=True)
					preds.append(float(m.forecast(1).iloc[0]))
				except Exception:
					pass
			# AR (AutoReg) with small lag
			if AutoReg is not None:
				try:
					m = AutoReg(series, lags=5, old_names=False).fit()
					preds.append(float(m.forecast(1).iloc[0]))
				except Exception:
					pass
			# ARIMA(1,1,1) as a simple differenced model
			if ARIMA is not None:
				try:
					m = ARIMA(series, order=(1, 1, 1)).fit()
					preds.append(float(m.forecast(1).iloc[0]))
				except Exception:
					pass

		if not preds:
			return 0.0, 0.0

		yhat = float(np.median(preds))  # robust aggregate
		last = float(series.iloc[-1])
		if last <= 0:
			return 0.0, 0.0

		pred_return = (yhat - last) / last
		# Strength = size of predicted move relative to 1% (clipped to [0,1])
		pred_strength = max(0.0, min(1.0, abs(pred_return) / 0.01))

		return float(pred_return), float(pred_strength)
	except Exception:
		return 0.0, 0.0


