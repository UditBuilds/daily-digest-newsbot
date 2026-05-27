import logging

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT

logger = logging.getLogger(__name__)


def _format_articles(articles):
    lines = []
    grouped = {}
    for a in articles:
        grouped.setdefault(a["category"], []).append(a)

    for cat, items in grouped.items():
        lines.append(f"### Category: {cat}")
        for a in items[:20]:
            lines.append(f"- [{a['source']}] {a['title']}")
            if a["summary"]:
                lines.append(f"  Summary: {a['summary']}")
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
        max_tokens=1500,
    )
    return resp.choices[0].message.content.strip()
