from aiogram import Router
from .start_handler import start_handler


def register_handlers(dp: Router):
    dp.include_router(start_handler)
