from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_menu_kb() -> InlineKeyboardMarkup:
    """
    Cоздаёт кнопку старта регистрации нового пользователя.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        InlineKeyboardMarkup: Клавиатура с кнопкой старта регистрации.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text='начать 🚀', callback_data='start_registration')
    return kb.as_markup(resize_keyboard=True)


def class_num_choose_kb() -> InlineKeyboardMarkup:
    """
    Cоздаёт клавиатуру выбора цифры класса.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        InlineKeyboardMarkup: Клавиатура выбора цифры класса.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text='10', callback_data='10')
    kb.button(text='11', callback_data='11')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def class_letter_choose_kb(cl_num: str) -> InlineKeyboardMarkup:
    """
    Cоздаёт клавиатуру выбора буквы класса в зависимости от выбранной ранее цифры класса.

    Аргументы:
        cl_num (str): Цифра класса, выбранная пользователем ранее.

    Возвращает:
        InlineKeyboardMarkup: Клавиатура выбора буквы класса.
    """
    classes_11 = [('В(бета)', 'В'), ('Η(эта)', 'Η'), ('Ζ(дзeта)', 'Ζ'), ('Θ(тета)', 'Θ'), ('Г(гамма)', 'Г'),
                  ('Ε(эпсилон)', 'Ε'), ('Ι(йота)', 'Ι'), ('К(каппа)', 'К'), ('Δ(дельта)', 'Δ'), ('Λ(лямбда)', 'Λ')]
    classes_10 = [('Μ(мю)', 'Μ'), ('Σ(сигма)', 'Σ'), ('Ξ(кси)', 'Ξ'), ('Τ(тау)', 'Τ'), ('Ο(омикрон)', 'Ο'),
                  ('Φ(фи)', 'Φ'), ('Π(пи)', 'Π'), ('Х(хи)', 'Х'), ('Ρ(ро)', 'Ρ'), ('Ψ(пси)', 'Ψ')]
    classes = classes_10 if cl_num == '10' else classes_11
    kb = InlineKeyboardBuilder()
    for class_name, class_letter in classes:
        kb.button(text=class_name, callback_data=class_letter)
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def class_group_choose_kb() -> InlineKeyboardMarkup:
    """
    Cоздаёт клавиатуру выбора группы класса.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        InlineKeyboardMarkup: Клавиатура выбора группы класса.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text='Группа А', callback_data='0')
    kb.button(text='Группа Б', callback_data='1')
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def uday_group_choose_kb(cl_num) -> InlineKeyboardMarkup:
    """
    Cоздаёт клавиатуру выбора группы универ-дня.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        InlineKeyboardMarkup: Клавиатура выбора группы универ-дня.
    """
    kb = InlineKeyboardBuilder()
    i, j = (6, 5) if cl_num == '11' else (7, 6)
    for n in range(1, i):
        kb.button(text=str(n), callback_data=str(n))
        kb.button(text=str(n + j), callback_data=str(n + j))
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)


def data_confirmation_kb() -> InlineKeyboardMarkup:
    """
    Создаёт клавиатуру подтверждения или повторного заполнения данных пользователя.

    Аргументы:
        None: функция ничего не принимает.

    Возвращает:
        InlineKeyboardMarkup: Клавиатура подтверждения данных или повторной регистрации.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text='Заполнить заново ⬅️', callback_data='restart')
    kb.button(text='Подтвердить ✅ ', callback_data='confirm')
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
