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

## Deployment (Render.com Free Tier)

The included `render.yaml` makes deployment to Render seamless.

1. Copy `.env.example` to `.env` and configure your variables
2. Push your code to GitHub (ensure `.env` is NOT committed).
3. Log into [Render.com](https://render.com/) and click **New > Blueprint**.
4. Connect your GitHub repository and let Render create the Web Service.
5. Once created, go to your Web Service dashboard and click the **Environment** tab on the left menu.
6. In **Environment Variables**, insert key-value pair of PYTHON_VERSION and 3.9.13.
7. Click **Add Secret File**, set the filename to `.env` and paste the entire contents of your local `.env` file into the editor box.
8. Save the secret file and restart your Web Service.

**Keeping the Bot Awake (Free Tier workaround):**
Render's Free Tier spins down Web Services after 15 minutes of inactivity. To bypass this and keep your bot running 24/7:

1. Create a free account on [UptimeRobot](https://uptimerobot.com/).
2. Click **Add New Monitor**.
3. Select **HTTP(s)** as the Monitor Type.
4. Paste your public Render URL with the `/healthz` path (e.g., `https://stock-alerter.onrender.com/healthz`).
5. Set the monitoring interval to **10 minutes** and save.
   UptimeRobot will ping your server every 10 minutes, preventing Render from ever putting it to sleep.

## Deployment (Oracle Cloud Always Free VM)

1. Sign up for [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/).
2. Launch an "Always Free" Compute Instance.
   - Select the standard **Ubuntu 22.04** Operating System Image (avoid the "minimal" version).
   - Select the default **AMD VM.Standard.E2.1.Micro** instance.
   - In the **Networking** section, check **"Assign a public IPv4 address"** to allow your server to connect to the public internet.
   - Download the SSH private key when creating the instance, and save it to `~/.ssh/`.
3. In terminal (e.g., Terminal on Mac or Command Prompt on Windows), secure SSH private key if not already done:
   ```bash
   chmod 400 ~/.ssh/<your-private-key>.key
   ```
   Then, SSH into your new VM:
   ```bash
   ssh -i ~/.ssh/<your-private-key>.key ubuntu@<your-vm-public-ip>
   ```
4. Install `pyenv` prerequisites, Git, and Screen:
   ```bash
   sudo apt update
   sudo apt install -y make build-essential libssl-dev zlib1g-dev \
   libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
   libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev git screen
   ```
   If a screen pops up asking "Which services should be restarted?", just press **Enter** key to accept the default `OK`.
5. Install `pyenv` and set Python to 3.9.13:
   ```bash
   curl https://pyenv.run | bash
   export PATH="$HOME/.pyenv/bin:$PATH"
   eval "$(pyenv init -)"
   pyenv install 3.9.13
   pyenv global 3.9.13
   ```
   Note: The `pyenv install` step downloads and compiles Python from scratch. On a Free Tier micro VM, this can take 10 to 20 minutes to complete.
6. Clone your repository:
   ```bash
   git clone <your_github_repo_url>
   cd Stock-Alerts
   ```
7. Create your `.env` file and insert your configuration:
   ```bash
   nano .env
   ```
   To save and exit the nano editor, press `Ctrl + X`, then press `Y`, and hit `Enter`.
8. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
9. Start a `screen` session. This allows the bot to keep running in the background even after you close your SSH terminal:
   ```bash
   screen -S stock-alert-bot
   ```
10. Run the bot:
    ```bash
    python main.py
    ```
11. You can now safely detach from the screen session by pressing `Ctrl + A` and then `D`. Your bot is now running 24/7 in the cloud.
    (To resume the session later and see the logs, type `screen -r stock-alert-bot`.)

## Updating Code or Configuration on Oracle Cloud

Because Oracle Cloud is a raw virtual machine, it will _not_ automatically sync when you push new code to GitHub. If you update your code or want to change your `.env` variables, you must manually pull the changes and restart the bot:

1. SSH back into your VM.
2. Re-attach to the bot's background session:
   ```bash
   screen -r stock-alert-bot
   ```
3. Press `Ctrl + C` to stop the bot from running.
4. **If updating code:** Run `git pull` to fetch your latest changes from GitHub.
5. **If updating config:** Open your `.env` file, make changes, and save (`Ctrl + X`, `Y`, `Enter`):
   ```bash
   nano .env
   ```
6. Start the bot back up:
   ```bash
   python main.py
   ```
7. Detach and leave it running in the background again (`Ctrl + A`, then `D`).

## Automated CI/CD (GitHub Actions)

If you are deploying on Oracle Cloud, you can configure GitHub to automatically deploy your new code every time you push to the `main` branch.

1. Ensure the `.github/workflows/deploy.yml` file is committed and pushed to your repository.
2. Go to your repository on github.com, click **Settings** > **Secrets and variables** > **Actions**.
3. Click **New repository secret** and add the following three secrets:
   - `ORACLE_HOST`: Your Oracle VM's Public IP address.
   - `ORACLE_USERNAME`: `ubuntu`
   - `ORACLE_SSH_KEY`: The entire contents of your private `.key` file.

Once configured, GitHub will automatically SSH into your server, gracefully stop the bot, pull the new code, install any new dependencies, and restart the bot in the background!
