from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from aiogram.enums import ParseMode

from src.config.settings import settings


async def setup_bot() -> Bot:
    bot: Bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        )
    )
    await bot.delete_webhook(drop_pending_updates=True)

    await bot.send_message(settings.ADMIN_TG_ID, 'bot started')

    return bot


__all__ = ["setup_bot"]

