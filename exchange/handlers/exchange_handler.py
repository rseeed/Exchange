from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

from exchange.utils.some_utils import connect_to_redis, read_redis, convert_currency

exchange_handler = Router()


@exchange_handler.message(Command('exchange'))
async def command_exchange_handler(message: Message, command: CommandObject):
    response_error_text = ('<b>An example of using this command:</b>\n'
                           '<code>/exchange USD RUB 10</code>\n\n'
                           'This command will convert 10 USD to RUB\n'
                           'The list of all available currencies is available by the command /rates')

    if not command.args:
        await message.answer(response_error_text)
        return

    args = command.args.split()

    if len(args) != 3:
        await message.answer(response_error_text)
        return

    redis_client = connect_to_redis()
    rate_1, rate_2 = read_redis(redis_client, args[0], args[1])
    if rate_1 is not None and rate_2 is not None:
        converted_rate = convert_currency(args[0], float(rate_1), args[1], float(rate_2), float(args[2]))
        response_text = f'<b>{args[2]} {args[0]} = {round(converted_rate, 3)} {args[1]}</b>'

        await message.answer(response_text)
    else:
        await message.answer(response_error_text)
