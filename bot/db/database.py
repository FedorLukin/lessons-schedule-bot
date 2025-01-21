from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from bot.config import load_db_URL


class DatabaseConnector:
    """
    Класс-декоратор создания сессий подключения к бд

    Этот класс позволяет декорировать функции выполняющие запрос к базе данных
    и создавать для них синхронные или асинхронные сессии.

    Атрибуты:
        engine (AsyncEngine | Engine): Асинхронный или синхронный движок SQLAlchemy.
        session_maker (async_sessionmaker | sessionmaker): Асинхронная или синхронная фабрика сессий SQLAlchemy.

    Методы:
        async_connection(method):
            Декоратор для создания асинхронного подключения к базе данных.

        regular_connection(method):
            Декоратор для создания синхронного подключения к базе данных.

        __call__(func):
            Декоратор, который выбирает тип соединения для указанной функции.
    """
    def __init__(self, connection_is_async=True) -> None:
        """
        Конструктор класса для создания движка и генератора сессий.

        Создаёт синхронный или асинхронный движок и генератор сессий
        в зависимости от переданного аргумента.

        Аргументы:
            connection_is_async (bool, optional): Тип подключения, асинхронное или нет. По умолчанию равен True.

        Возвращает:
            None: Метод ничего не возвращает.
        """
        self.connection_is_async = connection_is_async
        if connection_is_async:
            self.engine = create_async_engine(url=f'postgresql+asyncpg{load_db_URL()}')
            self.session_maker = async_sessionmaker(bind=self.engine, expire_on_commit=False)
        else:
            self.engine = create_engine(url=f'postgresql+psycopg2{load_db_URL()}')
            self.session_maker = sessionmaker(bind=self.engine, expire_on_commit=False)

    def async_connection(self, method):
        """
        Декоратор для создания асинхронного подключения к базе данных.

        Этот декоратор оборачивает асинхронную функцию, обеспечивая управление
        сессией базы данных: открытие, выполнение запроса и закрытие сессии.
        В случае возникновения исключения, транзакция будет отменена.

        Аргументы:
            method (coroutine): Асинхронная функция, которая выполняет запрос к базе данных.
                                Ожидается, что она принимает сессию в качестве первого аргумента.

        Возвращает:
            coroutine: Обёрнутую функцию.

        Исключения:
            Все исключения, возникающие при выполнении метода, будут перехвачены. 
            В случае ошибки транзакция будет откатана, а сессия закрыта.
        """
        async def wrapper(*args, **kwargs):
            async with self.session_maker() as session:
                try:
                    return await method(session, *args, **kwargs)
                except Exception as ex:
                    await session.rollback()
                    raise ex
                finally:
                    await session.close()
        return wrapper

    def regular_connection(self, method):
        """
        Декоратор для создания синхронного подключения к базе данных.

        Этот декоратор оборачивает синхронную функцию, обеспечивая управление
        сессией базы данных: открытие, выполнение запроса и закрытие сессии.
        В случае возникновения исключения, транзакция будет отменена.

        Аргументы:
            method (callable): Cинхронная функция, которая выполняет запрос к базе данных.
                               Ожидается, что она принимает сессию в качестве первого аргумента.

        Возвращает:
            callable: Обёрнутую функцию.

        Исключения:
            Все исключения, возникающие при выполнении метода, будут перехвачены. 
            В случае ошибки транзакция будет откатана, а сессия закрыта.
        """
        def wrapper(*args, **kwargs):
            with self.session_maker() as session:
                try:
                    return method(session, *args, **kwargs)
                except Exception as ex:
                    session.rollback()
                    raise ex
                finally:
                    session.close()
        return wrapper

    def __call__(self, func):
        """
        Декоратор, который выбирает тип соединения для указанной функции.

        Данный метод позволяет использовать экземпляр класса как декоратор.
        В зависимости от того, является ли соединение асинхронным или
        синхронным, он перенаправляет вызов к соответствующему методу:
        async_connection для асинхронных соединений и regular_connection
        для синхронных.

        Аргументы:
            func (callable): Функция, которую необходимо декорировать.
                             ожидается, что она будет принимать сессию базы данных
                             в качестве первого аргумента.

        Возвращает:
            callable: Обернутый метод, который будет использовать правильный
                      тип соединения при вызове.
        """
        return self.async_connection(func) if self.connection_is_async else self.regular_connection(func)
