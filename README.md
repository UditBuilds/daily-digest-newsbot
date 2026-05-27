# Daily Digest NewsBot

A personal news digest bot that sends a formatted, AI-summarized news briefing to a Telegram chat at **6:00 AM IST** and **6:00 PM IST** every day.

Covers: Geopolitics · AI / Tech · D2C & Indian startups · Science & Space.

## Stack

- Python 3.10+
- `feedparser` — RSS parsing
- `groq` — LLaMA 3.3-70B summarization (free tier)
- `python-telegram-bot` — Telegram delivery
- `APScheduler` — IST scheduling
- Deployable on Railway

## Project layout

```
bot.py              # entrypoint + scheduler
config.py           # env vars, RSS feeds, system prompt
fetcher.py          # RSS fetch + 12h filter + cleanup
summarizer.py       # Groq LLaMA 3.3-70B call
telegram_sender.py  # Telegram delivery (chunked)
requirements.txt
Procfile            # Railway worker
.env.example
```

## Setup

### 1. Create a Telegram bot

1. Open Telegram, search **@BotFather**, send `/newbot`.
2. Pick a name and username. BotFather returns a **bot token** — save it.
3. Send any message to your new bot from your personal account so it can DM you.
4. Get your **chat ID**:
   - Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Find `"chat":{"id":<number>}` in the JSON — that's your chat ID.
   - (For a group, add the bot to the group and look for the negative-numbered chat ID.)

### 2. Get a Groq API key

- Sign up at https://console.groq.com
- Create an API key from the dashboard. Free tier is enough.

### 3. Configure env vars

Copy `.env.example` to `.env` and fill in:

```
GROQ_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

### 4. Run locally

```bash
pip install -r requirements.txt
python bot.py                  # starts scheduler
python bot.py --run-now morning  # fire one digest immediately (for testing)
python bot.py --run-now evening
```

## Deploy on Railway

1. Push this project to GitHub.
2. On https://railway.app, **New Project → Deploy from GitHub repo**.
3. After deploy, open **Variables** and set:
   - `GROQ_API_KEY`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Railway reads the `Procfile` and runs `worker: python bot.py`. Make sure the service type is **worker** (not web — no port is exposed).
5. Confirm logs show: `Scheduler started. Morning 06:00 IST, Evening 18:00 IST.`

The container stays running and APScheduler triggers at 06:00 and 18:00 Asia/Kolkata.

## How it works

1. At 06:00 / 18:00 IST, all RSS feeds in `config.RSS_FEEDS` are fetched.
2. Only articles published in the **last 12 hours** are kept (feeds without timestamps are kept by default).
3. Headlines + summaries are grouped by category and sent to Groq (LLaMA 3.3-70B) with the briefing system prompt.
4. The model returns a clean digest grouped by category. Empty categories are skipped silently by the prompt.
5. The final message is sent to your Telegram chat, chunked if longer than 4000 chars.

## Customization

- **Feeds**: edit `RSS_FEEDS` in `config.py`.
- **Lookback window**: change `LOOKBACK_HOURS`.
- **Schedule**: edit the cron entries in `bot.main()`.
- **Prompt / tone**: edit `SYSTEM_PROMPT` in `config.py`.
