import time
import schedule
import config
from data_fetcher import fetch_data
from strategies import ut_bot
from discord_alert import send_discord_message, send_discord_error
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask
import threading
import os
import sys

# Dictionary to keep track of the last signal for each ticker to prevent duplicate alerts.
last_signals = {ticker: None for ticker in config.UT_BOT_TICKERS}

def is_within_bot_working_hours():
    """Checks if the current time is within the bot work hours defined in the config."""
    edt_tz = ZoneInfo("America/New_York")
    now = datetime.now(edt_tz)
    current_time = now.strftime("%H:%M")
    return config.START_TIME_EDT <= current_time <= config.END_TIME_EDT

def sleep_until_bot_working_hours():
    """Calculates time until the next start time and sleeps."""
    edt_tz = ZoneInfo("America/New_York")
    now = datetime.now(edt_tz)
    start_hour, start_minute = map(int, config.START_TIME_EDT.split(':'))
    
    target_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
    
    # If we are past the start time today, the next start time is tomorrow.
    if now >= target_time:
        target_time += timedelta(days=1)
        
    sleep_seconds = (target_time - now).total_seconds()
    print(f"Outside of bot working hours ({config.START_TIME_EDT} - {config.END_TIME_EDT} EDT). Sleeping until {target_time.strftime('%Y-%m-%d %H:%M:%S %Z')}.")
    time.sleep(sleep_seconds)

def job():
    print(f"Running scheduled check for {len(config.UT_BOT_TICKERS)} tickers: {config.UT_BOT_TICKERS}...")
    for ticker in config.UT_BOT_TICKERS:
        try:
            # We fetch using configured interval and period
            df = fetch_data(ticker, interval=config.UT_BOT_FETCH_DATA_INTERVAL, period=config.UT_BOT_FETCH_DATA_PERIOD)
            if df is None or df.empty:
                print(f"No data returned for {ticker}.")
                continue
                
            df = ut_bot(
                df, 
                sensitivity=config.UT_BOT_SENSITIVITY, 
                atr_period=config.UT_BOT_ATR_PERIOD,
                use_heikin_ashi=config.UT_BOT_USE_HEIKIN_ASHI
            )
            
            # Check the latest candle
            latest = df.iloc[-1]
            
            signal = None
            if latest['Buy']:
                signal = 'Buy'
            elif latest['Sell']:
                signal = 'Sell'
                
            if signal and last_signals[ticker] != signal:
                # New signal detected
                print(f"New {signal} signal for {ticker} at {latest['Close']}.")
                send_discord_message(ticker, "UT Bot", signal, latest['Close'])
                last_signals[ticker] = signal
            else:
                print(f"No new signals for {ticker}. Latest position: {'Buy' if latest['Position'] == 1 else 'Sell' if latest['Position'] == -1 else 'None'}")
                
        except Exception as e:
            error_msg = f"Error processing {ticker}: {e}"
            print(error_msg)
            send_discord_error(error_msg)
            
        # Sleep for 2 seconds between tickers to avoid Yahoo Finance rate limits
        time.sleep(2)

def main():
    print("Starting UT Bot Alerter...")
    print(f"Configured to check every {config.CHECK_INTERVAL_MINUTES} minutes.")
    
    # Run once immediately if within bot working hours, else sleep until first start time
    if not is_within_bot_working_hours():
        sleep_until_bot_working_hours()
    job()
    
    # Schedule subsequent runs
    schedule.every(config.CHECK_INTERVAL_MINUTES).minutes.do(job)
    
    while True:
        if not is_within_bot_working_hours():
            sleep_until_bot_working_hours()
        else:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    # Setup a lightweight Flask app to keep the service alive on Render Free Tier
    app = Flask(__name__)
    
    @app.route("/")
    def index():
        return "UT Bot Alerter is running!"
        
    @app.route("/healthz")
    def healthz():
        if config.CONFIG_ERROR:
            return f"Configuration Error: {config.CONFIG_ERROR}", 500
        return "OK", 200
        
    def run_flask():
        # Render provides the port in the PORT environment variable
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

    # Start Flask in a background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Run the main bot logic
    main()

    # sys.exit(0)
    
