from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, exists

from .database import DatabaseConnector
from .models import User, Admin, Regular_schedule, Uday_schedule
from bot.misc.lesson import Lesson

from typing import List, Tuple
from datetime import date


@DatabaseConnector()
async def is_admin(session: AsyncSession, tg_id: int) -> bool:
    """
    Проверяет, является ли пользователь администратором.

    Параметры:
        session (AsyncSession): Сессия для работы с базой данных.
        tg_id (int): Уникальный идентификатор пользователя в Telegram.

    Возвращает:
        bool: True, если пользователь является администратором, иначе False.
    """
    return await session.scalar(exists().where(Admin.id == tg_id).select())


@DatabaseConnector()
async def set_admin(session: AsyncSession, tg_id: int) -> None:
    """
    Добавляет нового администратора в базу данных.

    Параметры:
        session (AsyncSession): Сессия для работы с базой данных.
        tg_id (int): Уникальный идентификатор пользователя в Telegram.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    new_admin = Admin(id=tg_id)
    await session.merge(new_admin)
    await session.commit()


@DatabaseConnector()
async def get_admins(session: AsyncSession) -> List[int]:
    """
    Получает список идентификаторов администраторов из базы данных.

    Параметры:
        session (AsyncSession): Сессия для работы с базой данных.

    Возвращает:
        List[int]: Список идентификаторов администраторов.
    """
    result = await session.execute(select(Admin.id))
    return list(result.scalars())


@DatabaseConnector()
async def set_user(session: AsyncSession, tg_id: int, class_letter: str, class_group: int, uday_group: int) -> None:
    """
    Добавляет нового пользователя в базу данных.

    Параметры:
        session (AsyncSession): Сессия для работы с базой данных.
        tg_id (int): Уникальный идентификатор пользователя в Telegram.
        class_letter (str): Буквенное обозначение класса пользователя.
        class_group (int): Номер группы пользователя.
        uday_group (int): Номер группы для универ-дня.

    Возвращает:
        None
    """
    new_user = User(id=tg_id, class_letter=class_letter, class_group=class_group, uday_group=uday_group)
    await session.merge(new_user)
    await session.commit()


@DatabaseConnector()
async def get_user(session: AsyncSession, tg_id: int) -> User | None:
    """
    Извлекает пользователя из базы данных по его Telegram ID.

    Параметры:
        session (AsyncSession): Сессия для работы с базой данных.
        tg_id (int): Уникальный идентификатор пользователя в Telegram.

    Возвращает:
        User | None: Объект пользователя или None, если пользователь не найден.
    """
    return await session.scalar(select(User).filter_by(id=tg_id))


@DatabaseConnector()
async def delete_user(session: AsyncSession, tg_id: int) -> None:
    """
    Удаляет пользователя из базы данных по его Telegram ID.

    Параметры:
        session (AsyncSession): Сессия для работы с базой данных.
        tg_id (int): Уникальный идентификатор пользователя в Telegram.

    Возвращает:
        None: функция ничего не возвращает.
    """
    user = await session.scalar(select(User).filter_by(id=tg_id))
    await session.delete(user)
    await session.commit()


@DatabaseConnector()
async def get_users(session: AsyncSession, class_num: str) -> List[int]:
    """
    Получает список уникальных идентификаторов пользователей по номеру класса.

    Параметры:
        session (AsyncSession): Сессия для работы с базой данных.
        class_num (str): Номер класса для фильтрации пользователей.

    Возвращает:
        List[int]: Список идентификаторов пользователей.
    """
    result = await session.execute(select(User.id).filter(User.class_letter.startswith(class_num)))
    return list(result.scalars())


@DatabaseConnector()
async def get_all_users(session: AsyncSession) -> List[int]:
    """
    Получает список всех уникальных идентификаторов пользователей.

    Параметры:
        session (AsyncSession): Сессия для работы с базой данных.

    Возвращает:
        List[int]: Список всех идентификаторов пользователей.
    """
    result = await session.execute(select(User.id))
    return list(result.scalars())


@DatabaseConnector()
async def check_schedule_existence(session: AsyncSession, today: date, tomorrow: date) -> Tuple[bool]:
    """
    Проверяет наличие расписания на текущий и следующий день.

    Параметры:
        session (AsyncSession): Сессия для работы с базой данных.
        today (date): Дата для проверки наличия расписания на сегодня.
        tomorrow (date): Дата для проверки наличия расписания на завтра.

    Возвращает:
        Tuple[bool, bool]: Кортеж, содержащий два булевых значения — наличие расписания на сегодня и завтра.
    """
    today_flag = await session.scalar(exists().where(Regular_schedule.date == today).select())
    tomorrow_flag = await session.scalar(exists().where(Regular_schedule.date == tomorrow).select())
    return (today_flag, tomorrow_flag)


@DatabaseConnector()
async def get_user_schedule(session: AsyncSession, letter: str, group: int, uday_group: int, date: date) -> List[str]:
    """
    Получает расписание пользователя на заданную дату.

    Параметры:
        session (AsyncSession): Сессия для работы с базой данных.
        letter (str): Буквенное обозначение класса пользователя.
        group (int): Номер группы пользователя.
        uday_group (int): Номер группы для универ-дня.
        date (date): Дата для получения расписания.

    Возвращает:
        List[str]: Список информации об уроках на указанную дату.
    """
    uday_lessons = []
    if letter.startswith('10') and date.weekday() == 0 or letter.startswith('11') and date.weekday() == 2:
        uday_lessons = await session.execute(select(Uday_schedule.lesson_info).where(
            Uday_schedule.uday_group == uday_group,
            Uday_schedule.date == date).order_by(Uday_schedule.lesson_number))
        uday_lessons = list(uday_lessons.scalars())
        group = 0

    regular_lessons = await session.execute(select(Regular_schedule.lesson_info).where(
        Regular_schedule.class_letter == letter,
        Regular_schedule.class_group == group,
        Regular_schedule.date == date).order_by(Regular_schedule.lesson_number))
    regular_lessons = list(regular_lessons.scalars())

    return uday_lessons + regular_lessons


@DatabaseConnector(connection_is_async=False)
def delete_old_schedules(session: Session, date: date) -> None:
    """
    Удаляет расписания, которые старше или равны заданной дате.

    Параметры:
        session (Session): Сессия для работы с базой данных.
        date (date): Дата, до которой необходимо удалить расписания.

    Возвращает:
        None: функция ничего не возвращает.
    """
    session.query(Regular_schedule).filter(Regular_schedule.date <= date).delete(synchronize_session=False)
    session.query(Uday_schedule).filter(Uday_schedule.date <= date).delete(synchronize_session=False)
    session.commit()


@DatabaseConnector(connection_is_async=False)
def delete_repeated_schedule(session: Session, date: date) -> None:
    """
    Удаляет повторяющееся расписание на заданную дату.

    Параметры:
        session (Session): Сессия для работы с базой данных.
        date (date): Дата для удаления повторяющегося расписания.

    Возвращает:
        None: функция ничего не возвращает.
    """
    if session.scalar(exists().where(Regular_schedule.date == date).select()):
        session.query(Regular_schedule).filter(Regular_schedule.date == date).delete(synchronize_session=False)
        session.query(Uday_schedule).filter(Uday_schedule.date == date).delete(synchronize_session=False)
        session.commit()


@DatabaseConnector(connection_is_async=False)
def add_regular_lessons(session: Session, lessons_list: List[Lesson]) -> None:
    """
    Добавляет список обычных уроков в базу данных.

    Параметры:
        session (Session): Сессия для работы с базой данных.
        lessons_list (List[Lesson]): Список объектов уроков для добавления.

    Возвращает:
        None: функция ничего не возвращает.
    """
    lessons_to_save = [Regular_schedule(lesson_number=lesson.num, lesson_info=lesson.info, date=lesson.date,
                       class_letter=lesson.class_letter, class_group=lesson.group_num) for lesson in lessons_list]

    session.add_all(lessons_to_save)
    session.commit()


@DatabaseConnector(connection_is_async=False)
def add_uday_lessons(session: Session, lessons_list: List[Lesson]) -> None:
    """
    Добавляет список уроков универ-дня в базу данных.

    Параметры:
        session (Session): Сессия для работы с базой данных.
        lessons_list (List[Lesson]): Список объектов уроков универ-дня для добавления.

    Возвращает:
        None: функция ничего не возвращает.
    """
    lessons_to_save = [Uday_schedule(lesson_number=lesson.num, lesson_info=lesson.info, date=lesson.date,
                       uday_group=lesson.group_num) for lesson in lessons_list]

    session.add_all(lessons_to_save)
    session.commit()
