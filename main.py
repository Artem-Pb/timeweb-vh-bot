import asyncio
import logging
import sys
import aiohttp

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

import config
from handlers import user_router

log_format ="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            "bot.log",
            encoding="utf-8"
        )
    ]
)
logging.getLogger("aiogram.event").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def startup(dispatcher: Dispatcher):
    session = aiohttp.ClientSession()
    dispatcher["http_session"] = session
    logger.info("Starting up")

async def shutdown(dispatcher: Dispatcher):
    session: aiohttp.ClientSession = dispatcher["http_session"]
    await session.close()
    logger.info("Shutting down")


async def main() -> None:
    session = AiohttpSession(proxy=config.PROXY_URL) if config.PROXY_URL else None
    bot = Bot(token=config.BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.startup.register(startup)
    dp.shutdown.register(shutdown)

    dp.include_router(user_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())