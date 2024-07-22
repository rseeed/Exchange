from dataclasses import dataclass


@dataclass
class Config:
    bot_token: str


def load_config() -> Config:
    return Config(
        bot_token='7169258886:AAE9J0St_A1M-sATsRhBZTWC5IUi6wgkh1Y'
    )
