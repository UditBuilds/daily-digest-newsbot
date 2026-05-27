import logging
from datetime import datetime

import pytz
from apscheduler.schedulers.blocking import BlockingScheduler

from config import IST_TIMEZONE, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, GROQ_API_KEY
from fetcher import fetch_all_articles
from summarizer import summarize
from telegram_sender import send_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

IST = pytz.timezone(IST_TIMEZONE)


def build_and_send(slot: str):
    now = datetime.now(IST)
    header_emoji = "🌅" if slot == "morning" else "🌆"
    title = "MORNING BRIEF" if slot == "morning" else "EVENING BRIEF"
    date_str = now.strftime("%a, %d %b %Y")

    logger.info("Running %s digest at %s IST", slot, now.isoformat())

    try:
        articles = fetch_all_articles()
    except Exception as e:
        logger.exception("Fetching failed: %s", e)
        return

    if not articles:
        logger.info("No articles found for %s digest. Skipping.", slot)
        return

    try:
        body = summarize(articles)
    except Exception as e:
        logger.exception("Summarization failed: %s", e)
        return

    if not body:
        logger.info("Empty summary for %s digest. Skipping.", slot)
        return

    sources = sorted({a["source"] for a in articles})
    sources_line = ", ".join(sources[:8])

    divider = "━" * 20

    message = (
        f"{header_emoji} **{title}** — {date_str}\n"
        f"{divider}\n"
        f"{body}\n"
        f"{divider}\n"
        f"Sources: {sources_line}"
    )

    send_message(message)
    logger.info("%s digest sent.", slot.capitalize())


def morning_job():
    build_and_send("morning")


def evening_job():
    build_and_send("evening")


def _check_env():
    missing = [k for k, v in {
        "GROQ_API_KEY": GROQ_API_KEY,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        "TELEGRAM_CHAT_ID": TELEGRAM_CHAT_ID,
    }.items() if not v]
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}")


def main():
    _check_env()
    scheduler = BlockingScheduler(timezone=IST)
    scheduler.add_job(morning_job, "cron", hour=6, minute=0, id="morning_brief")
    scheduler.add_job(evening_job, "cron", hour=18, minute=0, id="evening_brief")

    logger.info("Scheduler started. Morning 06:00 IST, Evening 18:00 IST.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--run-now":
        _check_env()
        slot = sys.argv[2] if len(sys.argv) > 2 else "morning"
        build_and_send(slot)
    else:
        main()
