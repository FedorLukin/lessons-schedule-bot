from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def admin_panel_inline_button() -> ReplyKeyboardMarkup:
    """
    Cоздаёт кнопку для вызова админ-панели.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        ReplyKeyboardMarkup: Клавиатура с кнопкой вызова админ-панели.
    """
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text='админ-панель 🔐'))
    return kb.as_markup(resize_keyboard=True)


def admin_panel_main_kb() -> InlineKeyboardMarkup:
    """
    Создааёт клавиатуру админ-панели.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        InlineKeyboardMarkup: Клавиатура админ-панели.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text='запустить рассылку  ✉️', callback_data='start_notification')
    kb.button(text='загрузить расписание    🗓', callback_data='add_schedule')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)


def back_to_admin_kb() -> InlineKeyboardMarkup:
    """
    Создаёт кнопку возврата к админ-панели.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопкой возврата к админ-панели.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text='назад', callback_data='back')
    return kb.as_markup(resize_keyboard=True)


def recievers_choose() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру выбора получателей рассылки или возврата к админ-панели.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        InlineKeyboardMarkup: Клавиатура выбора получателей рассылки.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text='10', callback_data='10 классы')
    kb.button(text='11', callback_data='11 классы')
    kb.button(text='отправить всем', callback_data='все классы')
    kb.button(text='назад', callback_data='back')
    kb.adjust(2, 1, 1)
    return kb.as_markup(resize_keyboard=True)


def notification_confirmation_kb() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру запуска или отмены рассылки.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        InlineKeyboardMarkup: Клавиатура или отмены рассылки.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text='назад', callback_data='back')
    kb.button(text='отправить', callback_data='send')
    kb.adjust(2)
    return kb.as_markup(resize_keyborad=True)
