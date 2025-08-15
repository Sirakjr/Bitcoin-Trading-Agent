from src.config import load_config
cfg = load_config()
print(cfg.env, cfg.google_sheet_id)