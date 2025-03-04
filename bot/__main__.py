from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from bot.db.requests import get_admins
from bot.create_bot import bot, dp

from cachetools import TTLCache

import asyncio
import logging
from dotenv import dotenv_values

errors_cache = TTLCache(maxsize=30, ttl=120)


async def start_bot() -> None:
    """
    Уведомляет админов и разработчиков о запуске бота, вызывает функцию запуска бота.

    Принимает:
        None: функция ничего не принимает.

    Возвращает:
        None: функция ничего не возвращает.
    """
    env_vars = dotenv_values(".env")
    devs_ids = list(map(int, env_vars['DEVELOPERS_IDS'].split(',')))
    admins_ids = await get_admins()
    admins_and_devs = set(admins_ids + devs_ids)
    for id in admins_and_devs:
        try:
            await bot.send_message(chat_id=id, text='бот запущен 🚀')
        except (TelegramForbiddenError, TelegramBadRequest):
            pass

    # Запуск бота
    await main()


async def main() -> None:
    """
    Настраивает логгирование, запускает бота, в случае ошибки перезапускает бота и логгирует ошибку.

    Принимает:
        None: функция ничего не принимает.

    Возвращает:
        None: функция ничего не возвращает.
    """
    while True:
        try:
            logs_format = '%(asctime)s - %(filename)s:%(lineno)d - %(message)s'
            logging.basicConfig(level=logging.ERROR, filename='logs.log', filemode='w', format=logs_format)
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)

        except Exception as ex:
            await dp.stop_polling()
            error_name = ex.__class__.__name__
            if not errors_cache.get(error_name):
                errors_cache[error_name] = True
                logging.error(ex)


if __name__ == '__main__':
    asyncio.run(start_bot())
