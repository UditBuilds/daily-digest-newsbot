import logging
import re

from datetime import datetime

import pytz
from groq import Groq

from archiver import save_brief
from config import GROQ_API_KEY, GROQ_MODEL, IST_TIMEZONE, SYSTEM_PROMPT
from dedup import add_headlines

logger = logging.getLogger(__name__)

IST = pytz.timezone(IST_TIMEZONE)

# Story headlines in the digest are wrapped in **bold**.
_HEADLINE_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_THEME_RE = re.compile(r"Today'?s Theme:\s*(.+)", re.IGNORECASE)
_TRENDING_RE = re.compile(r"(🔍\s*Trending Topics:)\s*(.*)", re.IGNORECASE | re.DOTALL)

# Generic words that must never appear in Trending Topics.
_GENERIC_TRENDING = {
    "analysis", "reports", "report", "data", "research", "trends", "updates",
    "update", "insights", "perspectives", "recommendations", "statistics",
    "graphs", "charts", "tables", "studies", "findings", "results",
    "conclusions", "suggestions", "ideas", "opinions", "views", "editorials",
    "articles", "columns", "blogs", "news", "story", "stories",
}
_MAX_TRENDING = 7


def _sanitize_trending(digest: str) -> str:
    """Replace a possibly-runaway Trending Topics line with a clean, deduped,
    capped one. Guards against the model's repetition-loop hallucination."""
    m = _TRENDING_RE.search(digest)
    if not m:
        return digest

    raw = m.group(2)
    seen = set()
    clean = []
    for token in raw.split("·"):
        t = token.strip().strip("*").strip()
        if not t or len(t) > 40:
            continue
        key = t.lower()
        if key in _GENERIC_TRENDING or key in seen:
            continue
        seen.add(key)
        clean.append(t)
        if len(clean) >= _MAX_TRENDING:
            break

    new_line = f"{m.group(1)} " + " · ".join(clean)
    # Trending Topics is the last line; drop anything the model ran on after it.
    return digest[:m.start()] + new_line


# Deterministic filler scrub. Longer patterns first so e.g. "will likely be"
# is removed whole before "will likely" can match a fragment. (pattern, repl).
_FILLER_SUBS = [
    (r"will likely be ", ""),
    (r"will likely ", ""),
    (r"is likely to ", ""),
    (r"are likely to ", ""),
    (r"in the coming months", ""),
    (r"in the coming weeks", ""),
    (r"in the coming days", ""),
    (r"is expected to ", ""),
    (r"are expected to ", ""),
    (r"aiming to ", ""),
    (r"with a focus on ", ""),
    (r"in order to ", "to "),
]


def _scrub_filler(digest: str) -> str:
    """Delete/replace the most common filler phrases, then tidy whitespace."""
    for pattern, repl in _FILLER_SUBS:
        digest = re.sub(pattern, repl, digest, flags=re.IGNORECASE)
    # Tidy artifacts left by deletions: collapse runs of spaces and remove
    # spaces left before sentence punctuation.
    digest = re.sub(r"[ \t]{2,}", " ", digest)
    digest = re.sub(r" +([.,;:])", r"\1", digest)
    return digest

CATEGORY_LABELS = {
    "geopolitics": "GEOPOLITICS",
    "ai": "AI & TECH",
    "ai_releases": "AI RELEASES",
    "india_business": "INDIA BUSINESS",
    "business": "INDIA BUSINESS",
    "india_news": "INDIA NEWS",
    "science": "SCIENCE & SPACE",
}

# Category display names used as headers inside the digest body.
_KNOWN_CATEGORIES = [
    "GEOPOLITICS", "AI & TECH", "AI RELEASES",
    "INDIA BUSINESS", "INDIA NEWS", "SCIENCE & SPACE",
]


def _clean_headline(text: str) -> str:
    return text.strip().lstrip("🔴🟡🔵 ").strip()


def _extract_headlines(digest: str):
    """Pull every **bolded** story headline out of the digest body."""
    headlines = []
    for match in _HEADLINE_RE.findall(digest):
        text = _clean_headline(match)
        if text:
            headlines.append(text)
    return headlines


def _extract_theme(digest: str) -> str:
    m = _THEME_RE.search(digest)
    return m.group(1).strip() if m else ""


def _extract_stories(digest: str):
    """Return [{category, headline}] by tracking category headers in the body."""
    stories = []
    current = "GENERAL"
    for raw in digest.splitlines():
        line = raw.strip()
        if not line:
            continue
        # Detect a category header line (emoji + label, no bold story text).
        upper = line.upper()
        matched_cat = next(
            (c for c in _KNOWN_CATEGORIES if c in upper and len(line) <= len(c) + 6),
            None,
        )
        if matched_cat and "**" not in line:
            current = matched_cat
            continue
        for h in _HEADLINE_RE.findall(line):
            headline = _clean_headline(h)
            if headline:
                stories.append({"category": current, "headline": headline})
    return stories


def _format_articles(articles):
    # Articles arrive already clustered (see fetcher), so each one carries a
    # source_count. Order each category by corroboration so the big stories
    # survive the per-category cap.
    grouped = {}
    for a in articles:
        grouped.setdefault(a["category"], []).append(a)

    lines = []
    for cat, items in grouped.items():
        label = CATEGORY_LABELS.get(cat, cat.upper())
        items = sorted(items, key=lambda a: a.get("source_count", 1), reverse=True)
        lines.append(f"### Category: {label}")
        # Cap per category to stay under Groq's 12K tokens/min limit. Items are
        # sorted by source_count so the most-corroborated stories survive.
        for a in items[:6]:
            count = a.get("source_count", 1)
            primary = a.get("sources", [a["source"]])[0]
            lines.append(f"- Source: {primary} (source_count: {count})")
            lines.append(f"  Title: {a['title']}")
            if a.get("summary"):
                lines.append(f"  Summary: {a['summary'][:160]}")
            if a.get("url"):
                lines.append(f"  URL: {a['url']}")
        lines.append("")
    return "\n".join(lines)


def summarize(articles, slot: str = "morning"):
    if not articles:
        return None

    client = Groq(api_key=GROQ_API_KEY)
    user_content = _format_articles(articles)

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.4,
        max_tokens=2000,
        # Penalise token repetition to break the Trending Topics runaway loop.
        frequency_penalty=0.6,
    )
    digest = resp.choices[0].message.content.strip()

    # Deterministic guard against the Trending Topics repetition hallucination.
    digest = _sanitize_trending(digest)

    # Strip the most common filler phrases the model still emits.
    digest = _scrub_filler(digest)

    # Record headlines so the next brief can skip these stories.
    add_headlines(_extract_headlines(digest))

    # Archive the brief for the weekly roundup.
    try:
        now = datetime.now(IST)
        save_brief({
            "date": now.strftime("%Y-%m-%d"),
            "slot": slot,
            "theme": _extract_theme(digest),
            "stories": _extract_stories(digest),
            "sources": sorted({s for a in articles for s in a.get("sources", [a.get("source", "")]) if s}),
            "sent_at": now.replace(microsecond=0).isoformat(),
        })
    except Exception as e:
        logger.warning("Failed to archive brief: %s", e)

    return digest
