from aiogram.fsm.state import State, StatesGroup


class RegistrationSteps(StatesGroup):
    """
    Класс группы состояний регистрации.
    """
    class_num_choose = State()
    class_letter_choose = State()
    class_group_choose = State()
    uday_group_choose = State()
    confirmation = State()
    final = State()


class AdminPanelPages(StatesGroup):
    """
    Класс группы состояний Админ-панели.
    """
    schedule_add = State()
    schedule_file_request = State()
    schedule_file_parsing = State()
    notification_recievers_choose = State()
    notification_content_request = State()
    notification_confirmation = State()
    notificaton_start = State()
