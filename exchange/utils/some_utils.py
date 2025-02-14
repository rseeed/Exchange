import aiohttp
import logging
import redis
import os
import xml.etree.ElementTree as xmlET

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(message)s',
                    handlers=[logging.FileHandler('some_utils.log'),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))


async def fetch(url='https://cbr.ru/scripts/XML_daily.asp'):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            logger.error(f'Ошибка считывания по {url}: {e}')
            logger.error(e)


async def read_fetch(content: str):
    data = xmlET.fromstring(content)
    currencies = []
    for currency in data.findall('Valute'):
        name = currency.find('CharCode').text
        rate = currency.find('Value').text
        currencies.append([name, rate])
    return currencies


def connect_to_redis():
    try:
        redis_client = redis.StrictRedis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

        if redis_client.ping():
            logger.info('Подключение к Redis успешно')
        return redis_client

    except Exception as e:
        logger.error(f'Ошибка подключения к Redis: {e}')
        return None


def pull_redis(redis_client: redis.client.Redis, name, value):
    try:
        redis_client.set(name, float(value.replace(',', '.')))
        logger.info(f'Для ключа "{name}" успешно установлено значение "{float(value.replace(",", "."))}"')
    except Exception as e:
        logger.error(f'Ошибка установки значения для ключа "{name}": {e}')


async def update_currency_rates():
    logger.info(f'Пошло обновление данных Redis')
    content = await fetch()
    if content:
        currencies = await read_fetch(content)
        redis_client = connect_to_redis()
        if redis_client:
            for name, value in currencies:
                pull_redis(redis_client, name, value)
            redis_client.close()
            logger.info(f'Подключение к Redis закрыто')


def read_redis(redis_client: redis.client.Redis, currency_1: str = None, currency_2: str = None):
    if currency_1 is None or currency_2 is None:
        try:
            cursor = '0'
            all_data = {}
            while cursor != 0:
                cursor, keys = redis_client.scan(cursor=cursor, match='*', count=100)
                for key in keys:
                    value = redis_client.get(key)
                    all_data[key] = value
            return all_data
        except Exception as e:
            logger.error(f'Ошибка чтения данных в Redis: {e}')
            return None
    else:
        try:
            value_1, value_2 = redis_client.get(currency_1), redis_client.get(currency_2)
            if value_1 is not None and currency_2 == 'RUB':
                return value_1, 1.0
            elif value_2 is not None and currency_1 == 'RUB':
                return 1.0, value_2
            elif currency_1 == 'RUB' and currency_2 == 'RUB':
                return 1.0, 1.0
            elif value_1 is not None and value_2 is not None:
                return value_1, value_2
            else:
                logger.info(f'Было запрошено значение "{currency_1}, {currency_2}", которое отсутствует в Redis')
                return None, None
        except Exception as e:
            logger.error(f'Ошибка чтения данных в Redis: {e}')
            return None, None


def convert_currency(currency_1: str, rate_1: float, currency_2: str, rate_2: float, amount: float):
    if currency_1 == 'RUB':
        return amount / rate_2
    elif currency_2 == 'RUB':
        return amount * rate_1
    else:
        convert_1 = convert_currency(currency_1, rate_1, 'RUB', rate_2, amount)
        return convert_currency('RUB', rate_1, currency_2, rate_2, convert_1)
