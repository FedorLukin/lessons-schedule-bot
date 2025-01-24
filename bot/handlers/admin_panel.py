from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message, ContentType
from aiogram import Bot, Router, F

from bot.keyboards.admin_panel_keyboards import *

from bot.middlewares.album_middlleware import AlbumMiddleware
from bot.middlewares.admin_filter import AdminAccessMiddleware

from bot.misc.parsing import Parser
from bot.misc.states import AdminPanelPages

from bot.db.requests import get_users_ids, get_all_users_ids, delete_user


import datetime as dt
import asyncio

router = Router()
router.message.middleware(AdminAccessMiddleware())
router.callback_query.middleware(AdminAccessMiddleware())
router.message.middleware(AlbumMiddleware())


@router.message(F.text == 'админ-панель 🔐')
async def admin_panel(message: Message, state: FSMContext) -> None:
    """
    Отправляет главную страницу админ-панели.

    Аргументы:
        message (Message): Сообщение от админа.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения временных данных.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await message.answer(text='Добро пожаловать в админ-панель!', reply_markup=admin_panel_kb())
    await state.clear()


@router.callback_query(F.data == 'back')
async def admin_panel_back(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Возвращает на главную страницу админ-панели с других страниц.

    Аргументы:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения временных данных.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    # Удаляем сообщения с запросом подтверждения рассылки, если они есть
    notification_data = await state.get_data()
    messages_to_delete = notification_data.get('to_delete')
    if isinstance(messages_to_delete, Message):
        await messages_to_delete.delete()
    elif messages_to_delete:
        for message in messages_to_delete:
            await message.delete()
    # Отправляем админ-панель, удалив при необходимости сообщение для рассылки
    if callback.message.content_type == ContentType.TEXT:
        await callback.message.edit_text(text='Добро пожаловать в админ-панель!', reply_markup=admin_panel_kb())
    else:
        await callback.message.delete()
        await callback.message.answer(text='Добро пожаловать в админ-панель!', reply_markup=admin_panel_kb())
    await state.clear()


@router.callback_query(F.data == 'add_schedule')
async def file_request(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Запрашивает .xlsx файл с расписанием.

    Аргументы:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения временных данных.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await state.set_state(AdminPanelPages.schedule_file_parsing)
    await callback.message.edit_text(text='отправьте .xlsx файл для загрузки расписания',
                                     reply_markup=back_to_admin_kb())


@router.callback_query(F.data == 'start_notification')
async def notification_recievers_choose(callback: CallbackQuery) -> None:
    """
    Запрашивает выбор адресатов для рассылки.

    Аргументы:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    await callback.message.edit_text(text='Выберите адресатов рассылки', reply_markup=recievers_choose_kb())


@router.callback_query(F.message.text == 'Выберите адресатов рассылки', F.data != 'back')
async def notification_message_request(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обрабатывает выбор адресатов для рассылки уведомлений, запрашивает сообщение для рассылки.

    Аргументы:
        callback (CallbackQuery): Объект обратного вызова, содержащий информацию о нажатой кнопке.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения данных.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    recievers = callback.data
    await state.update_data(recievers=recievers)
    await state.set_state(AdminPanelPages.notification_confirmation)
    await callback.message.edit_text(text='отправьте сообщение для дальнейшей рассылки')


@router.message(StateFilter(AdminPanelPages.notification_confirmation))
async def notification_message_confirm(message: Message, state: FSMContext, album: list = None) -> None:
    """
    Обрабатывает сообщение для рассылки, запрашивает у админа подтверждение рассылки.

    Аргументы:
        message (Message): Сообщение от админа.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения данных.
        album (list, optional): Список медиафайлов для отправки в альбоме. По умолчанию None.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    notification_data = await state.get_data()
    recievers = notification_data.get('recievers')
    default_caption = f'подтвердите отправку сообщения\nполучатели: {recievers}'

    if album:
        # Формируем альбом при его наличии, если есть подпись то добавялем её
        notification_text = album[0].caption if album[0].caption else ''
        album_builder = MediaGroupBuilder(caption=notification_text)

        for ms in album:
            if ms.photo:
                album_builder.add_photo(media=ms.photo[0].file_id)
            elif ms.video:
                album_builder.add_video(media=ms.video.file_id)

        # Собираем альбом и отправляем его, сохраняем информаию об альбоме в состоянии
        album = album_builder.build()
        msg = await message.answer_media_group(media=album, caption=notification_text)
        await state.update_data(to_delete=msg, content_type='album', file_id=album)
        await message.answer(text=default_caption, reply_markup=notification_confirmation_kb())

    else:
        # Если альбома нет, обрабатываем одиночное сообщение
        notification_text = message.caption or message.text or ''
        message_caption = f'{notification_text}\n{"_" * 38}\n{default_caption}'

        # В зависимости от типа содержимого отправляем соответствующее сообщение, сохраняем информацию в стостоянии
        match message.content_type:
            case ContentType.TEXT:
                await message.answer(text=message_caption,
                                     reply_markup=notification_confirmation_kb())
                await state.update_data(content_type='text')

            case ContentType.PHOTO:
                await message.answer_photo(photo=message.photo[0].file_id,
                                           caption=message_caption,
                                           reply_markup=notification_confirmation_kb())
                await state.update_data(content_type='photo', file_id=message.photo[0].file_id)

            case ContentType.VIDEO:
                await message.answer_video(video=message.video.file_id,
                                           caption=message_caption,
                                           reply_markup=notification_confirmation_kb())
                await state.update_data(content_type='video', file_id=message.video.file_id)

            case ContentType.DOCUMENT:
                await message.answer_document(document=message.document.file_id,
                                              caption=message_caption,
                                              reply_markup=notification_confirmation_kb())
                await state.update_data(content_type='document', file_id=message.document.file_id)

            case ContentType.VIDEO_NOTE:
                msg = await message.answer_video_note(video_note=message.video_note.file_id)
                await state.update_data(to_delete=msg, content_type='video_note', file_id=message.video_note.file_id)
                await message.answer(text=message_caption, reply_markup=notification_confirmation_kb())

            case ContentType.VOICE:
                await message.answer_voice(voice=message.voice.file_id, caption=message_caption,
                                           reply_markup=notification_confirmation_kb())
                await state.update_data(content_type='voice', file_id=message.voice.file_id)

    # Сохраняем текст уведомления в состоянии
    await state.update_data(text=notification_text if notification_text else '')
    await state.set_state(AdminPanelPages.notificaton_start)


@router.callback_query(F.data == 'send', StateFilter(AdminPanelPages.notificaton_start))
async def notifaction_start(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """
    Функция рассылки сообщения пользователям.

    Удаляет сообщения, связанные с подтверждением отправки, получает данные для рассылки,
    рассылает сообщение выбранным пользователям и информирует админа о статусе рассылки.

    Аргументы:
        callback (CallbackQuery): Объект обратного вызова с данными о запросе.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения временных данных.
        bot (Bot): Объект бота для отправки сообщений.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    notification_data = await state.get_data()

    # Удаляем сообщение(я) подтверждения рассылки
    messages_to_delete = notification_data.get('to_delete')
    await callback.message.delete()

    if isinstance(messages_to_delete, Message):
        await messages_to_delete.delete()
    elif messages_to_delete:
        for message in messages_to_delete:
            await message.delete()

    recievers = notification_data.get('recievers')
    notification_text = notification_data.get('text')
    content_type, file_id = notification_data.get('content_type'), notification_data.get('file_id')

    # Определяем номер класса и получаем список студентов, уведомляем админа о начале рассылки
    cl_num = recievers.split()[0]
    students = await get_users_ids(cl_num) if recievers != 'все классы' else await get_all_users_ids()
    msg = await callback.message.answer(text='рассылка в процессе\n' + '⬜️' * 10)
    rows_num = len(students)

    # Отправляем соответствующее сообщение в зависимости от типа контента
    for counter, student_id in enumerate(students, start=1):
        try:
            match content_type:
                case 'text':
                    await bot.send_message(chat_id=student_id, text=notification_text)
                case 'photo':
                    await bot.send_photo(chat_id=student_id, photo=file_id, caption=notification_text)
                case 'video':
                    await bot.send_video(chat_id=student_id, video=file_id, caption=notification_text)
                case 'document':
                    await bot.send_document(chat_id=student_id, document=file_id, caption=notification_text)
                case 'video_note':
                    await bot.send_video_note(chat_id=student_id, video_note=file_id)
                case 'voice':
                    await bot.send_voice(chat_id=student_id, voice=file_id, caption=notification_text)
                case 'album':
                    await bot.send_media_group(chat_id=student_id, media=file_id)

        # Удаляем пользователя из базы данных, если тот заблокировал бота
        except TelegramForbiddenError:
            await delete_user(student_id)

        percent = int(counter / rows_num * 100) // 10
        await msg.edit_text(text=f'рассылка в процессе\n{"🟩" * percent}{"⬜️" * (10 - percent)} {counter}/{rows_num}')

        # Задержка для избежения нарушения ограничений телеграма
        await asyncio.sleep(0.035)

    await msg.edit_text(text='Рассылка завершена✅')


@router.message(StateFilter(AdminPanelPages.schedule_file_parsing))
async def schedule_file_parsing(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Обрабатывает загрузку файла расписания в формате .xlsx и выполняет его парсинг.

    Если файл успешно загружен и распарсен, уведомляет пользователей о новом расписании,
    а также сохраняет результаты парсинга.

    Аргументы:
        message (Message): Сообщение, содержащее загруженный файл.
        state (FSMContext): Контекст состояния для управления состоянием админ-панели и хранения временных данных.
        bot (Bot): Объект бота для отправки сообщений.

    Возвращает:
        None: Функция ничего не возвращает.
    """
    # Проверяем, что сообщение содержит документ и файл имеет правильный формат
    if message.document and message.document.file_name.endswith('.xlsx'):
        file_name = message.document.file_name
        await bot.download(message.document.file_id, destination=f'./bot/uploads/{file_name}')
        parser = Parser(file_name)
        parsing_result = parser.parse()

        # Отправляем результат парсинга админу
        await message.answer(text=parsing_result)

        # Если парсинг прошел успешно, запускаем оповещение
        if parsing_result == 'Расписание сохранено успешно!':
            students = await get_all_users_ids()

            # Определяем день, на который загружено расписание
            if parser.date == dt.datetime.today().date():
                day = 'сегодня'
            elif parser.date == dt.datetime.today().date() + dt.timedelta(days=1):
                day = 'завтра'
            else:
                day = parser.date.strftime('%d.%m')

            # Уведомляем учеников о загрузке расписании
            for student_id in students:
                await bot.send_message(chat_id=student_id, text=f'загружено расписание на {day}🗓')

                # Задержка для избежения нарушения ограничений телеграма
                await asyncio.sleep(0.035)
    else:
        await message.answer(text='Файл с расписанием должен быть формата .xlsx, попробуйте снова',
                             reply_markup=back_to_admin_kb())

    await state.clear()
