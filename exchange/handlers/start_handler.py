from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

start_handler = Router()


@start_handler.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer('Hello! I am an Exchange bot. Use my commands to simplify your life')
