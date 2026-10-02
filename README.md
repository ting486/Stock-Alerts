# Stock-Alerts

A Python application that uses different strategies (e.g.: UT Bot) to send buy/sell signals for selected stocks to a Discord channel.

- Fetches real-time(ish) data using Yahoo Finance API
- Computes buy/sell signals based on various strategies
- Supports Heikin Ashi candle charts
- Discord Webhook integration for rich embeds

## Architecture

- `main.py` - Main application loop, Flask server, and scheduling.
- `config.py` - Configuration parsing from `.env`.
- `data_fetcher.py` - Yahoo Finance integration.
- `strategies.py` - Core mathematical logic for UT Bot and ATR.
- `discord_alert.py` - Webhook functionality.

## Local Setup

To run the code locally:

1. Copy `.env.example` to `.env` and configure your variables
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```bash
   python main.py
   ```
   Note: You need to keep your machine on for the bot to work. You can also use cloud services like Render.com or Railway.com to run the bot 24/7 (see next section).

## Deployment (Render.com)

The included `render.yaml` makes deployment to Render seamless.

1. Copy `.env.example` to `.env` and configure your variables
2. Push your code to GitHub (ensure `.env` is NOT committed).
3. Log into [Render.com](https://render.com/) and click **New > Blueprint**.
4. Connect your GitHub repository and let Render create the Web Service.
5. Once created, go to your Web Service dashboard and click the **Environment** tab on the left menu.
6. In **Environment Variables**, insert key-value pair of PYTHON_VERSION and 3.9.13.
7. Click **Add Secret File**, set the filename to `.env` and paste the entire contents of your local `.env` file into the editor box.
8. Save the secret file and restart your Web Service.
