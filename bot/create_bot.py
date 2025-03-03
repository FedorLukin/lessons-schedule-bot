from bot.handlers import registration_callbacks, main_handlers, admin_panel, developer_panel

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher

from dotenv import dotenv_values


# Создаём экземпляры бота и диспетчера
env_vars = dotenv_values(".env")
bot = Bot(env_vars['BOT_TOKEN'])
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_routers(developer_panel.router, admin_panel.router, registration_callbacks.router,
                   main_handlers.router)
