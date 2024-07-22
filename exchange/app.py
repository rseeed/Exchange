import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import load_config
from handlers import register_handlers
from utils.some_utils import update_currency_rates

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='/rates', description='Current exchange rates'),
        BotCommand(command='/exchange', description='Transfer of currencies to other currencies')
    ]
    await bot.set_my_commands(commands)


async def on_startup(dispatcher: Dispatcher, bot: Bot):
    register_handlers(dispatcher)
    await set_commands(bot)
    await update_currency_rates()


async def daily_update_redis():
    logging.info('Обновление курс валют в Redis')
    await update_currency_rates()


scheduler.add_job(daily_update_redis, IntervalTrigger(days=1))


async def main():
    logging.basicConfig(level=logging.INFO)
    scheduler.start()
    config = load_config()

    bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    await on_startup(dp, bot)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.close()


if __name__ == '__main__':
    asyncio.run(main())
