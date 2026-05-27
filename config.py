import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

GROQ_MODEL = "llama-3.3-70b-versatile"

IST_TIMEZONE = "Asia/Kolkata"
LOOKBACK_HOURS = 12

RSS_FEEDS = [
    # Geopolitics
    {"name": "South China Morning Post", "url": "https://www.scmp.com/rss/91/feed", "category": "geopolitics"},
    {"name": "Reuters World", "url": "https://news.google.com/rss/search?q=site:reuters.com+world&hl=en-IN&gl=IN&ceid=IN:en", "category": "geopolitics"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/rss.xml", "category": "geopolitics"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "geopolitics"},
    {"name": "Google News Geopolitics", "url": "https://news.google.com/rss/search?q=geopolitics&hl=en-IN&gl=IN&ceid=IN:en", "category": "geopolitics"},
    # AI & Tech
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "ai"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "category": "ai"},
    {"name": "Google News AI", "url": "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-IN&gl=IN&ceid=IN:en", "category": "ai"},
    # India Business / D2C / Startups
    {"name": "Economic Times Markets", "url": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms", "category": "india_business"},
    {"name": "Inc42", "url": "https://inc42.com/feed/", "category": "india_business"},
    {"name": "Entrackr", "url": "https://entrackr.com/feed/", "category": "india_business"},
    {"name": "Google News India Business", "url": "https://news.google.com/rss/search?q=india+business+startup&hl=en-IN&gl=IN&ceid=IN:en", "category": "india_business"},
    {"name": "Google News India Startups", "url": "https://news.google.com/rss/search?q=india+startup+D2C&hl=en-IN&gl=IN&ceid=IN:en", "category": "india_business"},
    # Science & Space
    {"name": "Google News Science", "url": "https://news.google.com/rss/search?q=science+space&hl=en-IN&gl=IN&ceid=IN:en", "category": "science"},
]

SYSTEM_PROMPT = (
    "You are a sharp, no-fluff news analyst. Given a list of headlines and summaries, produce a clean news brief following these rules exactly:\n\n"
    "- Max 3 lines per story. Line 1: what happened (one crisp sentence). Line 2: why it matters. Line 3: what happens next or what to watch.\n"
    "- Zero filler words. Every word must carry information.\n"
    "- Rate each story: 🔴 Big Deal / 🟡 Worth Knowing / 🔵 FYI — place this tag at the start of the headline.\n"
    "- Add one 'Today's Theme' line at the very top of the brief summarising the overall mood of today's news in one sentence.\n"
    "- At the bottom add one line: 'Trending Topics:' followed by 3-5 keywords that define today's news.\n"
    "- Group stories by category. Skip any category with no significant news.\n"
    "- Max 8-10 stories total across all categories.\n"
    "- Output must be clean Telegram-formatted text using bold for headlines (wrap in **) and plain text for the 3 lines below.\n"
    "- For the single most important story in each category (the one tagged 🔴, or the top one if none is 🔴), append a line 'Read more → <url>' using the URL provided for that story. Do NOT add a Read more link for any other stories.\n"
    "- Do not invent URLs. Use only the URLs supplied in the input.\n\n"
    "Output format EXACTLY like this (skip a category entirely if no significant stories; categories must appear in this order):\n\n"
    "📌 Today's Theme: <one sentence>\n\n"
    "🌍 GEOPOLITICS\n"
    "🔴 **Headline**\n"
    "Line 1.\n"
    "Line 2.\n"
    "Line 3.\n"
    "Read more → <url>\n\n"
    "🤖 AI & TECH\n"
    "🟡 **Headline**\n"
    "Line 1.\n"
    "Line 2.\n"
    "Line 3.\n\n"
    "📦 INDIA BUSINESS\n"
    "🔵 **Headline**\n"
    "Line 1.\n"
    "Line 2.\n"
    "Line 3.\n\n"
    "🔬 SCIENCE & SPACE\n"
    "🔵 **Headline**\n"
    "Line 1.\n"
    "Line 2.\n"
    "Line 3.\n\n"
    "🔍 Trending Topics: keyword1 · keyword2 · keyword3\n"
    "\n"
    "The 📦 INDIA BUSINESS category covers D2C, Indian startups, funding rounds, and ecommerce trends.\n"
)
