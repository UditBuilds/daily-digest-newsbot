import logging
import re
from datetime import datetime, timedelta, timezone
from time import mktime

import feedparser

from config import RSS_FEEDS, LOOKBACK_HOURS

logger = logging.getLogger(__name__)

TAG_RE = re.compile(r"<[^>]+>")


def _clean(text: str) -> str:
    if not text:
        return ""
    return TAG_RE.sub("", text).strip()


def _entry_time(entry):
    for key in ("published_parsed", "updated_parsed"):
        t = entry.get(key)
        if t:
            try:
                return datetime.fromtimestamp(mktime(t), tz=timezone.utc)
            except Exception:
                continue
    return None


def fetch_all_articles():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)
    articles = []

    for feed in RSS_FEEDS:
        try:
            parsed = feedparser.parse(feed["url"])
            if parsed.bozo and not parsed.entries:
                logger.warning("Feed failed: %s (%s)", feed["name"], parsed.bozo_exception)
                continue

            for entry in parsed.entries[:25]:
                published = _entry_time(entry)
                if published and published < cutoff:
                    continue

                title = _clean(entry.get("title", ""))
                summary = _clean(entry.get("summary", "") or entry.get("description", ""))
                if not title:
                    continue

                url = entry.get("link", "") or entry.get("id", "")
                articles.append({
                    "source": feed["name"],
                    "category": feed["category"],
                    "title": title,
                    "summary": summary[:500],
                    "url": url,
                    "link": url,  # kept for backward compatibility
                    "published": published.isoformat() if published else "",
                })
        except Exception as e:
            logger.warning("Error fetching %s: %s", feed["name"], e)
            continue

    logger.info("Fetched %d articles in last %dh", len(articles), LOOKBACK_HOURS)
    return articles
