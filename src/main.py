"""
/**
 * @file: main.py
 * @description: Точка входа Telegram-бота для MVP
 * @dependencies: bot.handlers, infra.config.settings
 * @created: 2026-03-23
 */
"""

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers.admin import router as admin_router
from src.bot.handlers.appointment import router as appointment_router
from src.bot.handlers.booking import router as booking_router
from src.bot.handlers.start import router as start_router
from src.infra.config.settings import get_settings


def build_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(start_router)
    dispatcher.include_router(booking_router)
    dispatcher.include_router(appointment_router)
    dispatcher.include_router(admin_router)
    return dispatcher


async def main() -> None:
    settings = get_settings()
    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
    dispatcher = build_dispatcher()
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
