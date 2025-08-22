import warnings
import numpy as np
from statsmodels.tsa.arima.model import ARIMA



def forecast_next(candles_df):
	"""Forecast next close using ARIMA(1,1,2) only.

	Returns (pred_return, pred_strength) where pred_return is fractional return.
	Falls back to neutral (0, 0) if not enough data or model fails.
	"""
	try:
		if candles_df is None or candles_df.empty or "Close" not in candles_df.columns:
			return 0.0, 0.0
		series = candles_df["Close"].astype(float).tail(300)
		if len(series) < 20:
			return 0.0, 0.0

		with warnings.catch_warnings():
			warnings.simplefilter("ignore")
			model = ARIMA(series, order=(1, 1, 2)).fit()
			yhat = float(model.forecast(1).iloc[0])
		last = float(series.iloc[-1])
		if last <= 0:
			return 0.0, 0.0

		pred_return = (yhat - last) / last
		# Strength = size of predicted move relative to 1% (clipped to [0,1])
		pred_strength = max(0.0, min(1.0, abs(pred_return) / 0.01))

		return float(pred_return), float(pred_strength)
	except Exception:
		return 0.0, 0.0


