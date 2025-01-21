from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from aiohttp import web

from bot.handlers import registration_callbacks, main_handlers, admin_panel

from bot.config import BotConfig, load_bot_config, load_webhook_config

from cachetools import TTLCache

import logging

errors_cache = TTLCache(maxsize=20, ttl=120)
logs_format = '%(asctime)s - %(filename)s:%(lineno)d - %(message)s'
bot_config: BotConfig = load_bot_config()
webhook_config = load_webhook_config()

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 3001


async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(webhook_config.webhook_url)
    await bot.send_message(chat_id=bot_config.admin_ids[0], text='Бот запущен!!!')


async def on_shutdown(bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.send_message(chat_id=bot_config.admin_ids[0], text='Бот выключен!!!')


def main():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_routers(admin_panel.router, registration_callbacks.router, main_handlers.router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    bot = Bot(bot_config.token)
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=webhook_config.webhook_path)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR, filename='logs.log', filemode='w', format=logs_format)
    main()
