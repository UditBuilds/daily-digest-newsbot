"""Breaking-news alerter.

Fetches a small set of fast-moving feeds, asks Gemini whether any of the very
recent headlines counts as genuinely breaking, and pushes a Telegram alert if
so. Deduplicates against ``sent_alerts.json`` so we never alert on the same
headline twice within 24 hours.
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import pytz
from google import genai
from google.genai import types

from config import GEMINI_API_KEY, GEMINI_MODEL, IST_TIMEZONE
from fetcher import _clean, _entry_time
from telegram_sender import send_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

IST = pytz.timezone(IST_TIMEZONE)
ALERTS_FILE = Path("sent_alerts.json")
DEDUP_WINDOW = timedelta(hours=24)
MAX_REMEMBER = 10
LOOKBACK = timedelta(hours=2)

BREAKING_FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "https://news.google.com/rss/search?q=site:reuters.com+breaking&hl=en-IN&gl=IN&ceid=IN:en",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://news.google.com/rss/search?q=breaking+news+world&hl=en-IN&gl=IN&ceid=IN:en",
]

SYSTEM_PROMPT = (
    "You are a breaking news detector. Given these recent headlines, identify if ANY of them qualify as "
    "a genuine breaking news event. A genuine breaking event means: a war starting or major escalation, "
    "a head of state dying or being removed, a massive natural disaster affecting 100,000+ people, "
    "a major terror attack, a stock market crash of 3%+ in a major index, a major AI model release from "
    "OpenAI/Anthropic/Google/Meta, or a nuclear/chemical incident. "
    "If you find one, respond with exactly this JSON format: "
    '{"found": true, "headline": "exact headline", '
    '"summary": "two sentence summary of what happened and why it matters right now", '
    '"category": "GEOPOLITICS/AI/MARKETS/DISASTER"}. '
    'If nothing qualifies, respond with exactly: {"found": false}.'
)


def _fetch_recent():
    cutoff = datetime.now(timezone.utc) - LOOKBACK
    articles = []
    for url in BREAKING_FEEDS:
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries[:30]:
                t = _entry_time(entry)
                if t and t < cutoff:
                    continue
                title = _clean(entry.get("title", ""))
                if not title:
                    continue
                summary = _clean(entry.get("summary", "") or entry.get("description", ""))[:300]
                articles.append({"title": title, "summary": summary})
        except Exception as e:
            logger.warning("Breaking feed failed (%s): %s", url, e)
    logger.info("Fetched %d articles from breaking feeds in last %sh", len(articles), int(LOOKBACK.total_seconds() // 3600))
    return articles


def _load_sent():
    if not ALERTS_FILE.exists():
        return []
    try:
        return json.loads(ALERTS_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning("Could not read %s, treating as empty: %s", ALERTS_FILE, e)
        return []


def _save_sent(entries):
    ALERTS_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def _is_duplicate(headline: str, sent) -> bool:
    cutoff = datetime.now(timezone.utc) - DEDUP_WINDOW
    norm = headline.strip().lower()
    for entry in sent:
        try:
            ts = datetime.fromisoformat(entry["ts"])
        except Exception:
            continue
        if ts >= cutoff and entry.get("headline", "").strip().lower() == norm:
            return True
    return False


def _detect(articles):
    client = genai.Client(api_key=GEMINI_API_KEY)
    user = "\n".join(f"- {a['title']}: {a['summary']}" for a in articles[:40])
    resp = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
            max_output_tokens=400,
            response_mime_type="application/json",
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return json.loads(resp.text)


def main():
    missing = [k for k in ("GEMINI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID") if not os.getenv(k)]
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}")

    articles = _fetch_recent()
    if not articles:
        logger.info("No recent articles. Exiting.")
        return

    try:
        result = _detect(articles)
    except Exception as e:
        logger.exception("Breaking detection failed: %s", e)
        return

    if not result.get("found"):
        logger.info("No breaking news detected.")
        return

    headline = (result.get("headline") or "").strip()
    summary = (result.get("summary") or "").strip()
    category = (result.get("category") or "BREAKING").strip()

    if not headline:
        logger.info("Detector flagged breaking but no headline; skipping.")
        return

    sent = _load_sent()
    if _is_duplicate(headline, sent):
        logger.info("Already alerted on this headline within 24h: %s", headline)
        return

    now = datetime.now(IST)
    divider = "━" * 20
    message = (
        f"🚨 **BREAKING — {category}**\n"
        f"{divider}\n"
        f"{headline}\n\n"
        f"{summary}\n\n"
        f"⚡ Alert sent at {now.strftime('%H:%M')} IST"
    )

    send_message(message)
    logger.info("Breaking alert sent: %s", headline)

    sent.append({"headline": headline, "ts": datetime.now(timezone.utc).isoformat()})
    sent = sent[-MAX_REMEMBER:]
    _save_sent(sent)


if __name__ == "__main__":
    main()
