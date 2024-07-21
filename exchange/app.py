import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import load_config
from handlers import register_handlers

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(level=logging.INFO)
    config = load_config()

    bot = Bot(token=config.bot_token, parse_mode='HTML')
    dp = Dispatcher()

    register_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()


if __name__ == '__main__':
    asyncio.run(main())
