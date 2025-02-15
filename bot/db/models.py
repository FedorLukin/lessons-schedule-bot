from sqlalchemy import BigInteger, Integer, Text, String, Date
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

import datetime


class Base(AsyncAttrs, DeclarativeBase):
    """
    Абстрактный базовый класс для создания моделей.

    Этот класс служит основой для всех моделей в проекте, предоставляя
    общую функциональность и структуру. Он не предназначен для создания
    экземпляров.
    """
    __abstract__ = True


class Lesson(Base):
    """
    Абстрактный класс для моделей уроков в расписании.

    Этот класс наследуется от базового класса Base, определяет общие
    атрибуты для всех уроков, такие как идентификатор, номер урока,
    информация о уроке и дата. Не используется напрямую и служит основой
    для других моделей.
    """
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lesson_number: Mapped[int] = mapped_column(Integer, nullable=False)
    lesson_info: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date, nullable=False)


class Regular_schedule(Lesson):
    """
    Модель для обычного расписания уроков.

    Этот класс наследует от Lesson и добавляет атрибуты, специфичные
    для обычного расписания: буква класса и группа класса.
    """
    __tablename__ = 'regular_schedule'
    class_letter: Mapped[str] = mapped_column(String(5), nullable=False)
    class_group: Mapped[int] = mapped_column(Integer, nullable=False)


class Uday_schedule(Lesson):
    """
    Модель для расписания на универ-день.

    Этот класс наследует от Lesson и добавляет атрибут, специфичный
    для расписания универ-дня - группу универ-дня.
    """
    __tablename__ = 'uday_schedule'
    uday_group: Mapped[int] = mapped_column(Integer, nullable=False)


class User(Base):
    """
    Модель пользователя.

    Этот класс представляет пользователей бота и включает атрибуты
    буквы класса, группы класса и группы универ-дня. Каждый пользователь
    имеет уникальный идентификатор.
    """
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
    class_letter: Mapped[str] = mapped_column(String(5), nullable=False)
    class_group: Mapped[int] = mapped_column(Integer, nullable=False)
    uday_group: Mapped[int] = mapped_column(Integer, nullable=False)


class Admin(Base):
    """
    Модель администратора бота.

    Этот класс представляет админитратора бота, включает только идентификатор админа.
    Необходим для определения наличия у пользователя прав администратора.
    """
    __tablename__ = 'admins'
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
