import os
import json
from pathlib import Path
from dotenv import load_dotenv

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

CACHE_PATH = Path("config/settings_cache.json")


def _cast(value: str):
    text = (value or "").strip()
    if text.lower() in ("true", "false"):
        return text.lower() == "true"
    try:
        return int(text) if "." not in text else float(text)
    except ValueError:
        return text


def _read_sheet_overrides(sheet_id: str, tab: str, sa_json_path: str) -> dict:
    try:
        from google.oauth2.service_account import Credentials
        import gspread

        creds = Credentials.from_service_account_file(sa_json_path, scopes=SCOPES)
        ws = gspread.authorize(creds).open_by_key(sheet_id).worksheet(tab)
        rows = ws.get_all_values()
        overrides: dict = {}
        for row in rows:
            if not row:
                continue
            key = (row[0] or "").strip()
            if not key or key.startswith("#"):
                continue
            val = (row[1] if len(row) > 1 else "").strip()
            overrides[key] = _cast(val)
        return overrides
    except Exception:
        return {}


def load_config() -> dict:
    """Load .env, then override with Google Sheet (fallback to local cache)."""
    load_dotenv(".env")

    cfg = {
        # Runtime
        "ENV": os.getenv("ENV", "dev"),
        "LOG_LEVEL": os.getenv("LOG_LEVEL", "INFO"),

        # Coinbase
        "COINBASE_API_KEY": os.getenv("COINBASE_API_KEY", ""),
        "COINBASE_API_SECRET": os.getenv("COINBASE_API_SECRET", ""),
        "COINBASE_BASE_URL": os.getenv("COINBASE_BASE_URL", "https://api.coinbase.com"),
        "COINBASE_API_PASSPHRASE": os.getenv("COINBASE_API_PASSPHRASE", ""),

        # Google Sheets
        "GOOGLE_SHEET_ID": os.getenv("GOOGLE_SHEET_ID", ""),
        "GOOGLE_SHEET_TAB": os.getenv("GOOGLE_SHEET_TAB", "Config"),
        "GOOGLE_SERVICE_ACCOUNT_JSON_PATH": os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON_PATH", ""),

        # Telegram
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID", ""),

        # Gmail
        "GMAIL_USER": os.getenv("GMAIL_USER", ""),
        "GMAIL_APP_PASSWORD": os.getenv("GMAIL_APP_PASSWORD", ""),

        # LLM
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", ""),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "HF_MODEL_NAME": os.getenv("HF_MODEL_NAME", ""),

        # Strategy (defaults)
        "BUDGET_USD": _cast(os.getenv("BUDGET_USD", "10000")),
        "DCA_AMOUNT_USD": _cast(os.getenv("DCA_AMOUNT_USD", "500")),
        "DCA_DROP_PERCENT": _cast(os.getenv("DCA_DROP_PERCENT", "3.0")),
        "ATR_MULTIPLIER": _cast(os.getenv("ATR_MULTIPLIER", "1.5")),
        "DATA_FETCH_INTERVAL_MIN": _cast(os.getenv("DATA_FETCH_INTERVAL_MIN", "30")),
        "REPORT_CRON": os.getenv("REPORT_CRON", "0 9 * * 1"),
    }

    # Best-effort remote overrides → save cache; else try cache.
    sheet_id = cfg["GOOGLE_SHEET_ID"]
    sa_json = cfg["GOOGLE_SERVICE_ACCOUNT_JSON_PATH"]
    tab = cfg["GOOGLE_SHEET_TAB"]

    overrides = {}
    if sheet_id and sa_json and Path(sa_json).exists():
        overrides = _read_sheet_overrides(sheet_id, tab, sa_json)
        if overrides:
            CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with CACHE_PATH.open("w", encoding="utf-8") as f:
                json.dump(overrides, f, indent=2)

    if not overrides and CACHE_PATH.exists():
        try:
            with CACHE_PATH.open("r", encoding="utf-8") as f:
                overrides = json.load(f)
        except Exception:
            overrides = {}

    for k, v in overrides.items():
        if k in cfg:
            cfg[k] = v

    return cfg

