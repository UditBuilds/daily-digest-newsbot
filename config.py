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
    {"name": "South China Morning Post", "url": "https://www.scmp.com/rss/91/feed", "category": "geopolitics"},
    {"name": "Reuters World", "url": "https://news.google.com/rss/search?q=site:reuters.com+world&hl=en-IN&gl=IN&ceid=IN:en", "category": "geopolitics"},
    {"name": "BBC News", "url": "http://feeds.bbci.co.uk/news/rss.xml", "category": "geopolitics"},
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "geopolitics"},
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "ai"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml", "category": "ai"},
    {"name": "Google News Geopolitics", "url": "https://news.google.com/rss/search?q=geopolitics&hl=en-IN&gl=IN&ceid=IN:en", "category": "geopolitics"},
    {"name": "Google News AI", "url": "https://news.google.com/rss/search?q=artificial+intelligence&hl=en-IN&gl=IN&ceid=IN:en", "category": "ai"},
    {"name": "Google News India Startups", "url": "https://news.google.com/rss/search?q=india+startup+D2C&hl=en-IN&gl=IN&ceid=IN:en", "category": "business"},
    {"name": "Google News Science", "url": "https://news.google.com/rss/search?q=science+space&hl=en-IN&gl=IN&ceid=IN:en", "category": "science"},
]

SYSTEM_PROMPT = (
    "You are a sharp, concise news analyst. Given these headlines and summaries, "
    "create a clean briefing. Group by category. For each story write: one line "
    "headline, two line summary of what happened and why it matters. Skip fluff. "
    "Only include verified, significant stories. Max 8-10 stories total. Use simple language.\n\n"
    "Output format EXACTLY like this (skip a category entirely if no significant stories):\n\n"
    "🌍 GEOPOLITICS\n"
    "• [Headline]\n"
    "  [2 line summary]\n\n"
    "🤖 AI & TECH\n"
    "• [Headline]\n"
    "  [2 line summary]\n\n"
    "📈 BUSINESS & STARTUPS\n"
    "• [Headline]\n"
    "  [2 line summary]\n\n"
    "🔬 SCIENCE & SPACE\n"
    "• [Headline]\n"
    "  [2 line summary]\n"
)
