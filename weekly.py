"""Weekly 'Week in Review' roundup, generated from the brief archive."""

import logging
import os
from datetime import datetime, timedelta

import pytz
from groq import Groq

from archiver import load_recent_briefs
from config import GROQ_API_KEY, GROQ_MODEL, IST_TIMEZONE
from telegram_sender import send_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

IST = pytz.timezone(IST_TIMEZONE)

SYSTEM_PROMPT = (
    "You are a sharp weekly analyst. Given headlines and themes from the past 7 days, write a Week in Review.\n"
    "STRUCTURE:\n"
    "📌 Week in One Line: Exactly 2 sentences. Must name at least 3 specific entities (countries, companies, people). No vague statements.\n"
    "🏆 Top 3 Stories:\n"
    "Each story:\n"
    "WHAT: One sentence with specific facts — name, number, country, company.\n"
    "SO WHAT: One sentence — who is concretely affected and how.\n"
    "NEXT: One sentence — a specific named action, date, or decision coming. Never write 'expected to' or 'in the coming days' — if you don't know the next step, write what the two named parties will do based on the facts.\n"
    "🔭 Watch Next Week: 2-3 bullet points. Each must name a specific country, company, or person and a specific thing to watch for. Never write vague predictions.\n"
    "📊 This Week: One line. State which 2 categories dominated and give a specific example story from each. Format: 'Heavy on [Category] ([specific story]) · Moderate [Category] ([specific story])'\n"
    "BANNED: all the same banned phrases as the daily brief. Zero tolerance.\n\n"
    "Wrap each of the Top 3 headlines in **bold** and prefix it with its category in square brackets, "
    "e.g. '1. [GEOPOLITICS] **Headline**'."
)


def _build_input(briefs):
    lines = []
    themes = [b.get("theme", "") for b in briefs if b.get("theme")]
    if themes:
        lines.append("Daily themes this week:")
        lines.extend(f"- {t}" for t in themes)
        lines.append("")

    lines.append("Headlines by category this week:")
    by_cat = {}
    for b in briefs:
        for s in b.get("stories", []):
            by_cat.setdefault(s.get("category", "GENERAL"), []).append(s.get("headline", ""))
    for cat, heads in by_cat.items():
        lines.append(f"### {cat} ({len(heads)} stories)")
        lines.extend(f"- {h}" for h in heads if h)
        lines.append("")
    return "\n".join(lines)


def _week_range_label(now):
    start = now - timedelta(days=6)
    if start.month == now.month:
        return f"{start.strftime('%b %d')}–{now.strftime('%d, %Y')}"
    return f"{start.strftime('%b %d')}–{now.strftime('%b %d, %Y')}"


def main():
    missing = [k for k in ("GROQ_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID") if not os.getenv(k)]
    if missing:
        raise SystemExit(f"Missing env vars: {', '.join(missing)}")

    briefs = load_recent_briefs(days=7)
    if not briefs:
        logger.info("No briefs in the last 7 days. Skipping weekly roundup.")
        return

    total_stories = sum(len(b.get("stories", [])) for b in briefs)
    logger.info("Building weekly roundup from %d briefs (%d stories).", len(briefs), total_stories)

    client = Groq(api_key=GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_input(briefs)},
        ],
        temperature=0.4,
        max_tokens=2000,
    )
    body = resp.choices[0].message.content.strip()

    now = datetime.now(IST)
    divider = "━" * 20
    message = (
        f"📅 **WEEK IN REVIEW** — {_week_range_label(now)}\n"
        f"{divider}\n\n"
        f"{body}\n"
        f"{divider}"
    )
    send_message(message)
    logger.info("Weekly roundup sent.")


if __name__ == "__main__":
    main()
