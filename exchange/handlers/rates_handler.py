from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from exchange.utils.some_utils import connect_to_redis, read_redis

rates_handler = Router()


@rates_handler.message(Command('rates'))
async def command_rates_handler(message: Message):
    redis_client = connect_to_redis()
    currencies = read_redis(redis_client)
    redis_client.close()

    if currencies is None:
        response_text = '<b>The service is temporarily unavailable. Try it later</b>'
        await message.answer(response_text)
        return 0

    response_text = '<b>Current exchange rates:\n\n</b>'

    for key, value in currencies.items():
        response_text += f'<pre>{key} = {value} RUB  </pre>\n'

    await message.answer(response_text)
