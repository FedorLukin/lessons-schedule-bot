from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.filters import Command, StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F

from bot.keyboards.registration_keyboards import *
from bot.keyboards.main_keyboards import main_user_kb
from bot.keyboards.admin_panel_keyboards import admin_panels_kb

from bot.middlewares.throttling import ThrottlingMiddleware

from bot.db.requests import set_user, get_user
from dotenv import dotenv_values
from bot.misc.states import RegistrationSteps

router = Router()
router.message.middleware(ThrottlingMiddleware())


@router.message(Command('start'))
async def start(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает команду /start, если пользователь админ или разработчик,
    отправляем ему консоль админа или разработчика, иначе если пользователь
    не зарегистрирован - регистрируем.
    Переводит его в состояние выбора цифры класса.

    Аргументы:
        message (Message): Сообщение от пользователя.
        state (FSMContext): Контекст состояния для управления состоянием пользователя.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    env_vars = dotenv_values(".env")

    # Если пользователь админ или разработчик, приветствуем и отправляем консоль
    if message.from_user.id in set(map(int, env_vars['ADMIN_IDS'].split(',') + env_vars['DEVELOPERS_IDS'].split(','))):
        await message.answer(text=f'Здравствуйте, {message.from_user.first_name}! Вы являетесь администратором данного '
                                  f'бота и можете загружать расписание или запускать рассылку уведомлений, для этого '
                                  f'воспользуйтесь админ-панелью',
                             reply_markup=admin_panels_kb(message.from_user.id))

    # Если это обычный пользователь и он не зарегистрирован, запускаем регистрацию
    elif not await get_user(message.from_user.id):
        await state.set_state(RegistrationSteps.class_num_choose)
        await message.answer('Привет, давай определимся с твоими классом и группой', reply_markup=start_menu_kb())


@router.callback_query(F.data == 'start_registration', StateFilter(RegistrationSteps.class_num_choose))
async def class_num_choose(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает начало регистрации. Переводит пользователя в состояние выбора буквы класса.

    Аргументы:
        callback (CallbackQuery): Информация о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состоянием пользователя.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await state.set_state(RegistrationSteps.class_letter_choose)
    await callback.message.edit_text(text='Какой у тебя класс?', reply_markup=class_num_choose_kb())


@router.callback_query(F.message.text == 'Какой у тебя класс?', StateFilter(RegistrationSteps.class_letter_choose))
async def class_letter_choose(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает выбор буквы класса. Сохраняет номер класса и переводит пользователя в состояние выбора группы.

    Аргументы:
        callback (CallbackQuery): Информация о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состоянием пользователя.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    class_num = callback.data
    await state.update_data(num=class_num)
    await state.set_state(RegistrationSteps.class_group_choose)
    await callback.message.edit_text(text='А что насчёт буквы?', reply_markup=class_letter_choose_kb(class_num))


@router.callback_query(F.message.text == 'А что насчёт буквы?', StateFilter(RegistrationSteps.class_group_choose))
async def class_group_choose(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает выбор группы класса. Сохраняет букву класса и переводит пользователя
    в состояние выбора группы универдня.

    Аргументы:
        callback (CallbackQuery): Информация о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состоянием пользователя.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    class_letter = callback.data
    await state.update_data(letter=class_letter)
    await state.set_state(RegistrationSteps.uday_group_choose)
    await callback.message.edit_text(text='Теперь выбери свою группу класса', reply_markup=class_group_choose_kb())


@router.callback_query(F.message.text == 'Теперь выбери свою группу класса',
                       StateFilter(RegistrationSteps.uday_group_choose))
async def uday_group_choose(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает выбор группы класса. Сохраняет выбранную группу и переводит пользователя
    в состояние подтверждения данных.

    Аргументы:
        callback (CallbackQuery): Информация о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состоянием пользователя.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    user_data = await state.get_data()
    class_num = user_data.get('num')
    class_group = callback.data
    await state.update_data(cl_gr=class_group)
    await state.set_state(RegistrationSteps.confirmation)
    await callback.message.edit_text(text='Отлично, осталось выбрать группу универдня',
                                     reply_markup=uday_group_choose_kb(class_num))


@router.callback_query(F.message.text == 'Отлично, осталось выбрать группу универдня',
                       StateFilter(RegistrationSteps.confirmation))
async def data_confirmation(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Подтверждает введенные данные пользователя. Отправляет сообщение с проверкой введенных данных.

    Аргументы:
        callback (CallbackQuery): Информация о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состоянием пользователя.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    user_data = await state.get_data()
    class_num = user_data.get('num')
    class_letter = user_data.get('letter')
    class_group = 'группа А' if user_data.get('cl_gr') == '0' else 'Группа Б'
    uday_group = callback.data
    await state.update_data(ud_gr=uday_group)
    await state.set_state(RegistrationSteps.final)
    await callback.message.edit_text(text=f'🔎 Проверь, всё ли заполнено верно:\n📙 {class_num} {class_letter} класс,'
                                     f' {class_group}\n📗 {uday_group} группа универдня',
                                     reply_markup=data_confirmation_kb())


@router.callback_query(F.message.text.startswith('🔎 Проверь, всё ли заполнено верно:'),
                       StateFilter(RegistrationSteps.final))
async def final_or_restart_registration(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает финальную проверку данных. Позволяет перезапустить регистрацию или сохранить данные.

    Аргументы:
        callback (CallbackQuery): Информация о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состоянием пользователя.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    if callback.data == 'restart':
        await state.set_state(RegistrationSteps.class_letter_choose)
        await callback.message.edit_text(text='Какой у тебя класс?', reply_markup=class_num_choose_kb())
    else:
        user_data = await state.get_data()
        user_id = callback.from_user.id
        class_letter = f'{user_data.get("num")} {user_data.get("letter")}'
        class_group, uday_group = int(user_data.get('cl_gr')), int(user_data.get('ud_gr'))
        await set_user(user_id, class_letter, class_group, uday_group)
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(text='Успешно сохранено!', reply_markup=main_user_kb())
