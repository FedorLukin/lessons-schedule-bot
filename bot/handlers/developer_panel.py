from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram import Bot
from aiogram import Router, F

from bot.keyboards.admin_panel_keyboards import *

from bot.middlewares.admin_filter import AdminAccessMiddleware

from bot.db.requests import get_users, set_admin, get_admins

from bot.misc.states import DevPanelStates

from dotenv import dotenv_values

import datetime as dt
import sys


router = Router()
router.message.middleware(AdminAccessMiddleware())
router.callback_query.middleware(AdminAccessMiddleware())


@router.message(F.text == 'панель разработчика ⚙️')
async def developer_panel(message: Message, state: FSMContext) -> None:
    """
    Отправляет главную страницу панели разработчика.

    Аргументы:
        message (Message): Сообщение от разработчика.
        state (FSMContext): Контекст состояния для управления состоянием панели разработчика
                            и хранения временных данных.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await message.answer(text='Добро пожаловать в панель разработчика!', reply_markup=developer_panel_kb())
    await state.clear()


@router.callback_query(F.data == 'logs')
async def logs_stats(callback: CallbackQuery) -> None:
    """
    Подсчитывает количество ошибок за последние двое суток в логах и отправляет разработчику сообщение
    об их отсутствии или о их количестве.

    Аргументы:
        callback (CallbackQuery): Объект обратного вызова с данными о запросе.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await callback.message.delete()

    today_date = dt.date.today()
    yesterday_date = today_date - dt.timedelta(days=1)
    today, yesterday = today_date.strftime('%Y-%m-%d'), yesterday_date.strftime('%Y-%m-%d')

    # Считаем количество логов с датой в диапозоне двух суток
    with open('logs.log') as log_file:
        data = log_file.read()
        errors_today, errors_yesterday = data.count(today), data.count(yesterday)

    if errors_today or errors_yesterday:
        await callback.message.answer(text=f'⚠️отчёт об ошибках⚠️\nошибок сегодня: {errors_today}'
                                           f'\nошибок вчера: {errors_yesterday}')
    else:
        await callback.message.answer(text='за последние двое суток ошибок не было ✅')


@router.callback_query(F.data == 'stats')
async def users_stats(callback: CallbackQuery) -> None:
    """
    Отправляет данные об общем количестве пользователей бота и их распределении по классам.

    Отправляет главную страницу админ-панели.

    Аргументы:
        callback (CallbackQuery): Объект обратного вызова с данными о запросе.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await callback.message.delete()
    ten_class_users = len(await get_users('10'))
    eleven_class_users = len(await get_users('11'))
    await callback.message.answer(text=f'статистика по пользователям бота 📈\nпользователей всего:'
                                       f' {ten_class_users + eleven_class_users}\nучеников 10-х классов:'
                                       f' {ten_class_users}👩🏼‍💻\nучеников 11-х классов: {eleven_class_users}🧑🏼‍💻')


@router.callback_query(F.data == 'add_admin')
async def new_admin_id_request(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Запрашивает телеграм user id для назначения пользователя с соответствующим id администратором.

    Аргументы:
        callback (CallbackQuery): Объект обратного вызова с данными о запросе.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения временных данных.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await callback.message.delete()
    await callback.message.answer(text='отправьте телеграм user id пользователя, которого хотите назначить админом')
    await state.set_state(DevPanelStates.new_admin_request)


@router.message(StateFilter(DevPanelStates.new_admin_request))
async def add_new_admin_confirmation(message: Message, state: FSMContext) -> None:
    """
    Запрашивает подтверждение назначения пользователя админом если user id был указан корректно,
    иначе информирует об ошибке.

    Аргументы:
        message (Message): Сообщение от разработчика, содержащее телеграм user id нового админа.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения временных данных.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    user_id = message.text
    if user_id.isdigit():
        await state.update_data(id=str(user_id))
        await state.set_state(DevPanelStates.new_admin_adding)
        await message.answer(text=f'назначить пользователя с id: {message.text} администратором бота?\n\n'
                                  f'для подтверждения отправьте "confirm"')
    else:
        await message.answer(text='⚠️ неверный формат, user id должен быть числом ⚠️')


@router.message(F.text == 'confirm', StateFilter(DevPanelStates.new_admin_adding))
async def new_admin_adding(message: Message, state: FSMContext) -> None:
    """
    Сохраняет телеграм user id нового админа в переменную окружения, уведомляет разработчика о добавлении.

    Аргументы:
        message (Message): Сообщение от разработчика.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения временных данных.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    data = await state.get_data()
    new_admin_id = int(data['id'])
    await set_admin(new_admin_id)
    await message.answer(text='новый админ добавлен 📁')
    await state.clear()


@router.callback_query(F.data == 'stop_bot')
async def stop_bot_confirmation(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Запрашивает подтверждение остановки бота.

    Аргументы:
        message (Message): Сообщение от разработчика.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения временных данных.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await callback.message.delete()
    await callback.message.answer(text='вы уверены? для остановки бота отправьте "stop"')
    await state.set_state(DevPanelStates.stop_bot)


@router.message(F.text == 'stop', StateFilter(DevPanelStates.stop_bot))
async def stop_bot(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Останавливает бота, уведомляет админов и других разработчиков об остановке и кем она была произведена.

    Аргументы:
        message (Message): Сообщение от пользователя.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения временных данных.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await message.reply("Останавливаю бота...")
    admin_and_devs_ids = await get_admins()

    # Уведомляем админов и разрабов об остановке бота
    for id in admin_and_devs_ids:
        try:
            await bot.send_message(chat_id=id, text=f'бот приостановлен админом {message.from_user.first_name} ❗️')
        except TelegramForbiddenError:
            pass

    sys.exit(0)
