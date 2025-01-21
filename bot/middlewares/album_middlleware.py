import asyncio
from typing import Any, Dict, Union, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    """
    Middleware для обработки медиа-альбомов.

    Этот класс собирает сообщения, относящиеся к одной медиа-группе, и обрабатывает их с заданной задержкой.
    Он позволяет собирать сообщения, которые могут быть отправлены одновременно, и передавать их
    в обработчик после завершения сбора.

    Атрибуты:
        latency (Union[int, float]): Задержка в секундах перед обработкой сообщений одной медиа-группы.
        album_data (dict): Словарь для хранения собранных сообщений по media_group_id.

    Методы:
        collect_album_messages(event: Message) -> int:
            Собирает сообщения одной медиа-группы и возвращает общее количество сообщений в группе.

        __call__(handler, event: Message, data: Dict[str, Any]) -> Any:
            Основная логика, обрабатывающая входящие события и собирающая сообщения.
    """
    def __init__(self, latency: Union[int, float] = 0.15):
        """
        Конструктор класса.

        Аргументы:
            latency (Union[int, float], optional): Задержка в секундах, по умолчанию равна 0.15

        Возвращает:
            None: Метод ничего не возвращает.
        """
        self.latency = latency
        self.album_data = {}

    def collect_album_messages(self, event: Message) -> int:
        """
        Сбор сообщений одной медиа-группы.

        Аргументы:
            event (Message): Сообщение, содержащее данные о медиа-группе.

        Возвращает:
            int: общее количество сообщений в текущей медиа-группе.
        """
        # Проверка, существует ли media_group_id в album_data
        if event.media_group_id not in self.album_data:
            # Создание новой записи для медиа-группы
            self.album_data[event.media_group_id] = {"messages": []}

        # Добавление нового сообщения в медиа-группу
        self.album_data[event.media_group_id]["messages"].append(event)

        # Возврат общего количества сообщений в текущей медиа-группе
        return len(self.album_data[event.media_group_id]["messages"])

    async def __call__(self, handler: Callable, event: Message, data: Dict[str, Any]) -> Any:
        """
        Основная логика.

        Аргументы:
            handler (Callable): Исходный обработчик события.
            event (Message): Сообщение, которое нужно обработать.
            data (Dict[str, Any]): Дополнительные данные для обработки.

        Возвращает:
            Результат обработки события.
        """
        # Если у события нет media_group_id, сразу передаем его обработчику
        if not event.media_group_id:
            return await handler(event, data)

        # Сбор сообщений одной медиа-группы
        total_before = self.collect_album_messages(event)

        # Ожидание указанного времени задержки
        await asyncio.sleep(self.latency)

        # Проверка общего количества сообщений после задержки
        album_messages = self.album_data.get(event.media_group_id)

        # Если album_messages равно None, это означает, что медиа-группа была удалена
        if album_messages is None:
            return

        total_after = len(album_messages["messages"])

        # Если новые сообщения были добавлены во время задержки, выходим
        if total_before != total_after:
            return

        # Сортировка сообщений альбома по message_id и добавление в данные
        album_messages["messages"].sort(key=lambda x: x.message_id)
        data["album"] = album_messages["messages"]

        # Удаление медиа-группы из отслеживания для освобождения памяти
        del self.album_data[event.media_group_id]

        # Вызов оригинального обработчика события
        return await handler(event, data)
