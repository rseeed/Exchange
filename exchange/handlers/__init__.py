from aiogram import Router
from .start_handler import start_handler
from .rates_handler import rates_handler


def register_handlers(dp: Router):
    dp.include_router(start_handler)
    dp.include_router(rates_handler)
