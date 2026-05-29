# 🗞 Daily Digest NewsBot

> Twice-daily AI-summarized news briefing delivered to Telegram. Free forever.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Groq](https://img.shields.io/badge/LLM-Groq%20LLaMA%203.3--70B-orange)
![GitHub Actions](https://img.shields.io/badge/Automation-GitHub%20Actions-black)
![License](https://img.shields.io/badge/License-MIT-green)

## What it does
A fully automated personal news agent that fetches from 15+ RSS sources, filters and summarizes using LLaMA 3.3-70B via Groq, and delivers a clean brief to Telegram at 6:00 AM and 6:00 PM IST daily.

## Features
- 🌍 6 news categories: Geopolitics, AI & Tech, AI Releases, India Business, India News, Science & Space
- 🌤 Live Delhi weather via Open-Meteo
- 📊 Live market snapshot: Nifty, Sensex, USD/INR, Bitcoin
- 🚨 Breaking news alerts every 2 hours
- 📅 Weekly Sunday roundup
- 🔍 Feed health monitor every Monday
- ✅ Story deduplication across briefs
- 🔗 Source clustering — same story from multiple sources merged
- ⚡ Exact timing via cron-job.org (no GitHub Actions drift)
- 💰 Completely free forever

## Tech Stack
| Component | Technology |
|---|---|
| Language | Python 3.11 |
| LLM | Groq LLaMA 3.3-70B (free tier) |
| News Sources | RSS feeds via feedparser |
| Delivery | Telegram Bot API |
| Scheduling | cron-job.org → GitHub Actions repository_dispatch |
| Hosting | GitHub Actions (serverless) |
| Weather | Open-Meteo API (free, no key) |
| Markets | Yahoo Finance + ExchangeRate API + CoinGecko |

## News Sources (15+ feeds)
**Geopolitics:** SCMP, Al Jazeera, BBC News, Reuters via Google News
**AI & Tech:** TechCrunch AI, The Verge AI, Google News AI
**AI Releases:** OpenAI Blog, Google AI Blog, VentureBeat AI + Anthropic, DeepMind, Meta AI, Mistral, OpenAI, xAI via Google News
**India Business:** Inc42, YourStory, The Ken, Google News Startups
**India News:** Indian Express, The Hindu, Times of India, Google News India
**Science:** Google News Science

## Sample Output
```
🌅 MORNING BRIEF — Fri, 29 May 2026
━━━━━━━━━━━━━━━━━━━━
🌤 Delhi: 32°C · Clear Sky · Wind 12 km/h
📊 Nifty: 23,907 (closed) · Sensex: 75,868 (closed) · ₹/$ 84.1 · BTC $73,514
📌 Today's Theme: Anthropic hits $965B valuation while Israel escalates in Lebanon

🌍 GEOPOLITICS
🔴 Israel Declares New Combat Zone in Lebanon
...
```

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/Uditbuilds/daily-digest-newsbot
cd daily-digest-newsbot
pip install -r requirements.txt
```

### 2. Create a Telegram bot
- Message @BotFather → /newbot → copy the token
- Send any message to your new bot, then get your chat ID:
```
https://api.telegram.org/bot<TOKEN>/getUpdates
```

### 3. Get a free Groq API key
- Sign up at https://console.groq.com
- Create an API key (free tier: 100k tokens/day)

### 4. Set up environment variables
```bash
cp .env.example .env
# Fill in GROQ_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

### 5. Test locally
```bash
python bot.py --run-now morning
```

### 6. Deploy (free)
- Push to GitHub
- Add 3 secrets in repo Settings → Secrets → Actions
- Create two cron-job.org jobs (see below)

### 7. cron-job.org setup
Create two jobs at https://cron-job.org:

| Job | Schedule (UTC) | Body |
|---|---|---|
| Morning | 0:30 (= 6:00 IST) | `{"event_type": "morning_digest"}` |
| Evening | 12:30 (= 18:00 IST) | `{"event_type": "evening_digest"}` |

For both jobs:
- URL: `https://api.github.com/repos/YOUR_USERNAME/daily-digest-newsbot/dispatches`
- Method: POST
- Headers: `Authorization: Bearer YOUR_GITHUB_PAT` and `Accept: application/vnd.github+json` and `Content-Type: application/json`

## Project Structure
```
daily-digest-newsbot/
├── bot.py              # Entrypoint, scheduler, --run-now flag
├── fetcher.py          # RSS fetching with SSL-proof requests + feedparser
├── summarizer.py       # Groq API call + headline extraction + archiving
├── telegram_sender.py  # Async Telegram send with chunking
├── config.py           # RSS feeds, system prompt, env vars
├── dedup.py            # 24h story deduplication
├── clusterer.py        # Source clustering + importance scoring
├── archiver.py         # 90-day brief archive
├── weather.py          # Delhi weather via Open-Meteo
├── markets.py          # Nifty/Sensex/USD-INR/BTC data
├── breaking.py         # Breaking news detector
├── feed_monitor.py     # Weekly feed health checker
├── weekly.py           # Sunday week-in-review generator
└── .github/workflows/  # 4 GitHub Actions workflows
```

## Workflows
| Workflow | Trigger | What it does |
|---|---|---|
| `digest.yml` | cron-job.org 2x daily | Morning + evening brief |
| `breaking.yml` | Every 2 hours | Breaking news check |
| `feed_monitor.yml` | Every Monday | Feed health report |
| `weekly.yml` | Every Sunday | Week in review |

## Sister Project
🤖 [AI Intelligence Daily](https://github.com/Uditbuilds/AI-Intelligence-Daily) — founder-focused daily AI brief

## License
MIT
