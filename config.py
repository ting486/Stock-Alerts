import os
from dotenv import load_dotenv

load_dotenv()

def get_env_or_raise(key):
    val = os.getenv(key)
    if val is None:
        raise ValueError(f"Environment variable '{key}' is required but not found in .env")
    return val

CONFIG_ERROR = None

try:
    DISCORD_WEBHOOK_URL = get_env_or_raise("DISCORD_WEBHOOK_URL")
    DISCORD_MENTION = os.getenv("DISCORD_MENTION", "") # Optional: e.g., @everyone or <@user_id>

    # Parse TICKERS into a list.
    raw_tickers = get_env_or_raise("TICKERS")
    TICKERS = [t.strip() for t in raw_tickers.split(",") if t.strip()]

    # UT_BOT_TICKERS falls back to TICKERS if not provided
    raw_ut_bot_tickers = os.getenv("UT_BOT_TICKERS")
    if raw_ut_bot_tickers is not None:
        UT_BOT_TICKERS = [t.strip() for t in raw_ut_bot_tickers.split(",") if t.strip()]
    else:
        UT_BOT_TICKERS = TICKERS

    CHECK_INTERVAL_MINUTES = int(get_env_or_raise("CHECK_INTERVAL_MINUTES"))
    START_TIME_EDT = get_env_or_raise("START_TIME_EDT")
    END_TIME_EDT = get_env_or_raise("END_TIME_EDT")
    
    UT_BOT_SENSITIVITY = float(get_env_or_raise("UT_BOT_SENSITIVITY"))
    UT_BOT_ATR_PERIOD = int(get_env_or_raise("UT_BOT_ATR_PERIOD"))
    UT_BOT_USE_HEIKIN_ASHI = get_env_or_raise("UT_BOT_USE_HEIKIN_ASHI").lower() in ("true", "1", "yes")
    UT_BOT_FETCH_DATA_INTERVAL = get_env_or_raise("UT_BOT_FETCH_DATA_INTERVAL")
    UT_BOT_FETCH_DATA_PERIOD = get_env_or_raise("UT_BOT_FETCH_DATA_PERIOD")
    
    
except ValueError as e:
    CONFIG_ERROR = str(e)
    raise Exception(f"Configuration Error: {e}")
