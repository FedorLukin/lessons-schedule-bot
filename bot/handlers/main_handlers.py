from aiogram.fsm.context import FSMContext
from aiogram.filters import ChatMemberUpdatedFilter, KICKED
from aiogram.types import CallbackQuery, Message, ChatMemberUpdated
from aiogram import Router, F

from bot.keyboards.main_keyboards import *

from bot.middlewares.throttling import ThrottlingMiddleware

from bot.db.requests import check_schedule_existence, get_user, get_user_schedule, delete_user

from bot.misc.states import RegistrationSteps

import datetime as dt


router = Router()
router.message.outer_middleware(ThrottlingMiddleware())


@router.message(F.text == 'профиль 👤')
async def get_profile_info(message: Message, state: FSMContext) -> None:
    """
    Обрабатывает запрос на получение информации о профиле пользователя, если информация
    о пользователе есть в базе данных, отправляет ему его данные.

    Аргументы:
        message (Message): Сообщение, содержащее запрос на информацию о профиле.
        state (FSMContext): Контекст состояния для управления состоянием пользователя.

    Возвращает:
        None: функция ничего не возвращает.
    """
    user = await get_user(message.from_user.id)
    if user:
        class_group = 'группа А' if user.class_group == 0 else 'Группа Б'

        # Устанавливаем состояние для потворного заполнения данных
        await state.set_state(RegistrationSteps.class_num_choose)

        await message.answer(
            f'📚 Твои данные:\n📙 {user.class_letter} класс, {class_group}\n📗 {user.uday_group} группа '
            f'универдня',
            reply_markup=edit_data_kb()
        )


@router.message(F.text == 'расписание 📋')
async def schedule_day_choose(message: Message) -> None:
    """
    Обрабатывает запрос на выбор дня для получения расписания, если расписание на
    сегодня/завтра загружено, запрашивает выбор дня, иначе уведомляет об отсутствии
    расписания.

    Аргументы:
        message (Message): Сообщение, содержащее запрос на расписание.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    today = dt.datetime.today().date()
    tomorrow = today + dt.timedelta(days=1)
    today_flag, tomorrow_flag = await check_schedule_existence(today, tomorrow)
    if today_flag or tomorrow_flag:
        await message.answer('выбери интересующий день👇',
                             reply_markup=day_choose_kb(today_flag, tomorrow_flag, today, tomorrow))
    else:
        await message.answer('расписание ещё не загружено')


@router.callback_query(F.data.startswith('date='))
async def get_schedule(callback: CallbackQuery) -> None:
    """
    Обрабатывает запрос на получение расписания по выбранной дате.
    Извлекает из базы данных расписание в соответствие с данными пользователя и
    выбранной датой.

    Аргументы:
        callback (CallbackQuery): Объект обратного вызова, содержащий данные о выбранной дате.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    date = dt.datetime.strptime(callback.data.split('=')[1], '%d%m%y').date()
    user = await get_user(callback.from_user.id)
    lessons = await get_user_schedule(user.class_letter, user.class_group, user.uday_group, date)
    await callback.message.edit_text(text='\n\n'.join(lessons))


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def process_user_blocked_bot(event: ChatMemberUpdated):
    """
    Удаляет пользователя из базы данных, когда пользователь блокирует бота.

    Аргументы:
        event (ChatMemberUpdated): Событие обновления статуса пользователя.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await delete_user(event.from_user.id)
