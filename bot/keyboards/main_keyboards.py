from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from datetime import date


def edit_data_kb() -> InlineKeyboardMarkup:
    """
    Cоздаёт кнопку редактирования данных пользователя.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопкой редактирования данных.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text='изменить данные 📝', callback_data='start_registration')
    return kb.as_markup(resize_keyboard=True)


def main_user_kb() -> ReplyKeyboardMarkup:
    """
    Cоздаёт клавиатуру для просмотра данных пользователя и получения расписания.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        ReplyKeyboardMarkup: Клавиатура для просмотра данных и получения расписани.
    """
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='расписание 📋'))
    kb.add(KeyboardButton(text='профиль 👤'))
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def day_choose_kb(today_flag: bool, tomorrow_flag: bool, today: date, tomorrow: date) -> InlineKeyboardMarkup | None:
    """
    Создает клавиатуру для выбора даты (сегодня или завтра) для получения расписания.

    Аргументы:
        today_flag (bool): Флаг наличия расписания на сегодня.
        tomorrow_flag (bool): Флаг наличия расписания на завтра.
        today (date): Сегодняшняя дата.
        tomorrow (date): Завтрашняя дата.

    Возвращает:
        InlineKeyboardMarkup | None: Объект клавиатуры, если хотя бы одна кнопка доступна, иначе возвращает None.
    """
    if today_flag or tomorrow_flag:
        kb = InlineKeyboardBuilder()
        if today_flag:
            kb.button(text=f'сегодня {today.strftime('%d.%m')}', callback_data=f'date={today.strftime('%d%m%y')}')
        if tomorrow_flag:
            kb.button(text=f'завтра {tomorrow.strftime('%d.%m')}', callback_data=f'date={tomorrow.strftime('%d%m%y')}')
        kb.adjust(1)
        return kb.as_markup(resize_keyboard=True)
    return None
