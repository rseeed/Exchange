import aiohttp
import asyncio
import logging
import redis
import xml.etree.ElementTree as xmlET

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(message)s',
                    handlers=[logging.FileHandler('some_utils.log'),
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)


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


def connect_to_redis(host='localhost', port=6379):
    try:
        redis_client = redis.StrictRedis(
            host=host,
            port=port,
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
        redis_client.set(name, value)
        logger.info(f'Для ключа "{name}" успешно установлено значение "{value}"')
    except Exception as e:
        logger.error(f'Ошибка установки значения для ключа "{name}": {e}')


def read_redis(redis_client: redis.client.Redis):
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


async def main():
    content = await fetch()
    if content:
        currencies = await read_fetch(content)
        redis_client = connect_to_redis()
        if redis_client:
            for currency in currencies:
                pull_redis(redis_client, currency[0], currency[1])
            data = read_redis(redis_client)
            print(data)

            redis_client.close()
            logger.info('Подключение к Redis закрыто')
