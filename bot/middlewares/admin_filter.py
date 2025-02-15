from aiogram.types import Message
from aiogram import BaseMiddleware

from typing import Any, Awaitable, Callable, Dict

from bot.db.requests import is_admin


class AdminAccessMiddleware(BaseMiddleware):
    """
    Middleware для ограничения доступа к определенным модулям только для администраторов.

    Этот класс проверяет, является ли пользователь администратором, основываясь на его ID.
    Если пользователь не является администратором, обработчик не будет вызван.

    Атрибуты:
        None: У класса нет атрибутов.

    Методы:
        __call__(handler: Callable[[Message, Dict[str, Any]],
                 Awaitable[Any]],
                 message: Message,
                 data: Dict[str, Any]): Проверяет пользователя на наличие прав администратора.
    """
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: Dict[str, Any]
    ) -> Any:
        """
        Проверяет, является ли пользователь администратором.

        Аргументы:
            handler (Callable): Обработчик сообщения, который будет вызван, если пользователь - администратор.
            message (Message): Сообщение от пользователя, которое содержит информацию о пользователе.
            data (Dict[str, Any]): Дополнительные данные, которые могут быть переданы в обработчик.

        Возвращает:
            Any: Возвращает результат вызова обработчика, если пользователь - администратор, иначе возвращает None.
        """
        # Проверяем, является ли пользователь админом
        if not await is_admin(message.from_user.id):

            # Если пользователь не администратор, прерываем выполнение
            return None

        # Если пользователь администратор, вызываем обработчик
        return await handler(message, data)
