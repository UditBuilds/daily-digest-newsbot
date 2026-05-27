import asyncio
import logging

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

MAX_LEN = 4000


def _chunks(text):
    while text:
        if len(text) <= MAX_LEN:
            yield text
            return
        cut = text.rfind("\n", 0, MAX_LEN)
        if cut == -1:
            cut = MAX_LEN
        yield text[:cut]
        text = text[cut:].lstrip()


async def _send(message: str):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    for chunk in _chunks(message):
        try:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=chunk,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
        except TelegramError as e:
            logger.error("Telegram send failed: %s", e)


def send_message(message: str):
    asyncio.run(_send(message))
