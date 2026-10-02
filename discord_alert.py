import requests
import config

def send_discord_message(symbol, strategy_name, signal, price):
    if not config.DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL not configured.")
        return
        
    is_buy = signal.lower() == 'buy'
    color = 0x00FF00 if is_buy else 0xFF0000 # Green for Buy, Red for Sell
    
    try:
        embed = {
            "title": f"{strategy_name} Alert: {symbol}",
            "description": f"**{signal.upper()}** signal triggered for **{symbol}**.",
            "color": color,
            "fields": [
                {"name": "Price", "value": f"${price:.2f}", "inline": True},
                {"name": "Signal", "value": signal.upper(), "inline": True}
            ]
        }
        
        data = {
            "embeds": [embed]
        }
        if config.DISCORD_MENTION:
            data["content"] = config.DISCORD_MENTION
    
        response = requests.post(config.DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        print(f"Successfully sent Discord alert for {symbol}.")
    except Exception as e:
        error_msg = f"Failed to send Discord alert: {e}"
        print(error_msg)
        send_discord_error(error_msg)

def send_discord_error(error_message):
    if not config.DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL not configured.")
        return
        
    try:
        embed = {
            "title": "⚠️ Bot Error Alert",
            "description": str(error_message),
            "color": 0xFFA500 # Orange for warnings/errors
        }
        
        data = {
            "embeds": [embed],
            "content": "@everyone"
        }
        
        response = requests.post(config.DISCORD_WEBHOOK_URL, json=data)
        response.raise_for_status()
        print(f"Successfully sent Discord error alert.")
    except Exception as e:
        print(f"Failed to send Discord error alert: {e}")
