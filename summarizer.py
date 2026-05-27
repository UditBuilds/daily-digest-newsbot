import logging

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "geopolitics": "GEOPOLITICS",
    "ai": "AI & TECH",
    "india_business": "INDIA BUSINESS",
    "business": "INDIA BUSINESS",
    "science": "SCIENCE & SPACE",
}


def _format_articles(articles):
    grouped = {}
    for a in articles:
        grouped.setdefault(a["category"], []).append(a)

    lines = []
    for cat, items in grouped.items():
        label = CATEGORY_LABELS.get(cat, cat.upper())
        lines.append(f"### Category: {label}")
        for a in items[:8]:
            lines.append(f"- Source: {a['source']}")
            lines.append(f"  Title: {a['title']}")
            if a.get("summary"):
                lines.append(f"  Summary: {a['summary'][:220]}")
            if a.get("url"):
                lines.append(f"  URL: {a['url']}")
        lines.append("")
    return "\n".join(lines)


def summarize(articles):
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
    )
    return resp.choices[0].message.content.strip()
