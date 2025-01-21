from typing import Any, Awaitable, Callable, Dict
from cachetools import TTLCache
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message


CACHE = TTLCache(maxsize=400, ttl=4)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware для ограничения частоты запросов от пользователей.

    Этот middleware ограничивает количество запросов, которые пользователь может
    отправлять в определённый промежуток времени. При превышении лимита запросов
    пользователю отправляется уведомление с просьбой подождать.

    Атрибуты:
        CACHE (dict): Словарь для хранения количества запросов от каждого пользователя.

    Методы:
        __call__(handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                 message: Message,
                 data: Dict[str, Any]): Обработчик входящих сообщений.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            message: Message,
            data: Dict[str, Any]
    ) -> Any | None:
        """
        Обрабатывает входящие сообщения и ограничивает частоту запросов.

        Этот метод проверяет количество запросов от пользователя. Если количество
        запросов превышает допустимый лимит, пользователю отправляется сообщение с
        просьбой подождать. В противном случае запрос передаётся следующему обработчику.

        Аргументы:
            handler (Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]]):
                Функция-обработчик для обработки сообщения.
            message (Message): Объект сообщения от пользователя.
            data (Dict[str, Any]): Дополнительные данные, передаваемые в обработчик.

        Возвращает:
            Any | None: Результат выполнения обработчика, если запрос не превышает лимит, иначе None.
        """
        user_id = message.from_user.id
        current_count = CACHE.get(user_id, 0)

        if current_count > 1:
            return None

        CACHE[user_id] = current_count + 1

        if current_count == 1:
            await message.answer(text='подождите 5 секунд и повторите запрос')
            return

        return await handler(message, data)
