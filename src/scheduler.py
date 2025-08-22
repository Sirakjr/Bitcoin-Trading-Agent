from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from src.config.config_manager import load_config
from src.data.price_data import fetch_bitcoin_data
from src.ml.forecasting import forecast_next
from src.ml.threshold_adapter import adapt_thresholds, write_overrides
from src.main import run_once
from src.notify.email_report import send_weekly_report


sched = BlockingScheduler()


@sched.scheduled_job("interval", minutes=60, id="update_overrides")
def update_overrides_job():
	cfg = load_config()
	df = fetch_bitcoin_data()
	if df.empty:
		return
	pred_return, pred_strength = forecast_next(df)
	atr_value = 0.0  # not needed for mapping currently
	overrides = adapt_thresholds(cfg, pred_return, pred_strength, atr_value)
	overrides.update({
		"updated_at": datetime.now().isoformat(),
		"pred_return": pred_return,
		"pred_strength": pred_strength,
	})
	write_overrides(overrides)


@sched.scheduled_job("interval", minutes=30, id="trade_loop")
def trade_loop_job():
	run_once()


@sched.scheduled_job("cron", day_of_week="mon", hour=9, id="weekly_report")
def weekly_report_job():
	send_weekly_report()


def main():
	sched.start()


if __name__ == "__main__":
	main()


