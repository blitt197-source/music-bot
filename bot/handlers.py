"""
Обработчики команд и сообщений бота
"""
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import hashlib

from bot.keyboards import get_main_menu, get_search_results_keyboard, get_source_selection_keyboard, get_favorites_keyboard, get_track_actions_keyboard
from api.music_search import search_music, search_by_source
from api.downloader import MusicDownloader

router = Router()
router.db = None  # Будет установлено в main.py

# Глобальный загрузчик
downloader = MusicDownloader()

# Хранилище результатов поиска (временное)
search_results_cache = {}

# Хранилище запросов (для длинных запросов)
query_cache = {}


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Команда /start"""
    from config.settings import ADMIN_IDS
    
    # Добавляем пользователя в БД
    if router.db:
        await router.db.add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )
    
    # Проверяем является ли пользователь админом
    is_admin = message.from_user.id in ADMIN_IDS or message.chat.id in ADMIN_IDS
    
    welcome_text = """
🎵 <b>Добро пожаловать в Music Bot!</b>

Я помогу тебе найти и скачать любую музыку!

<b>🎯 Как пользоваться:</b>
1️⃣ Напиши название трека или исполнителя
2️⃣ Выбери источник поиска
3️⃣ Нажми на нужный трек
4️⃣ Получи MP3 файл!

<b>📍 Источники:</b>
🔵 <b>Deezer</b>
🟡 <b>Яндекс.Музыка</b>
🎵 <b>Music Original</b>

<i>Просто напиши название песни и начнём!</i>

@Music_good_bot
    """
    
    await message.answer(
        welcome_text,
        reply_markup=get_main_menu(is_admin=is_admin),
        parse_mode='HTML'
    )


@router.message(Command('help'))
async def cmd_help(message: Message):
    """Команда /help"""
    help_text = """
📖 <b>Как пользоваться ботом:</b>

1️⃣ Напиши название трека или исполнителя
2️⃣ Выбери нужный трек из результатов
3️⃣ Жди, пока я скачаю и отправлю тебе музыку

<b>Команды:</b>
/start - Главное меню
/help - Помощь

<b>Кнопки:</b>
❤️ Избранное - сохранённые треки
🎵 Рекомендации - топ-20 Яндекс.Музыки
    """
    
    await message.answer(help_text, parse_mode='HTML')


# Игнорируем все неизвестные команды
@router.message(F.text.startswith('/'))
async def ignore_unknown_commands(message: Message):
    """Игнорировать неизвестные команды"""
    # Просто не отвечаем
    pass


@router.message(F.text == "❤️ Избранное")
async def show_favorites(message: Message):
    """Показать избранное"""
    if not router.db:
        await message.answer("⚠️ База данных недоступна")
        return
    
    favorites = await router.db.get_favorites(message.from_user.id)
    
    if not favorites:
        await message.answer(
            "📝 <b>Твоё избранное пусто</b>\n\n"
            "Найди треки и добавь их в избранное кнопкой ❤️",
            parse_mode='HTML'
        )
        return
    
    # Формируем список
    text = f"❤️ <b>Твоё избранное ({len(favorites)} треков)</b>\n\n"
    
    for idx, fav in enumerate(favorites[:10], 1):
        text += f"{idx}. <b>{fav.track_artist}</b> - {fav.track_title}\n"
    
    if len(favorites) > 10:
        text += f"\n<i>И ещё {len(favorites) - 10} треков...</i>"
    
    await message.answer(
        text,
        reply_markup=get_favorites_keyboard(favorites),
        parse_mode='HTML'
    )


@router.message(F.text == "🎵 Рекомендации дня")
async def show_recommendations(message: Message):
    """Показать рекомендации - топ-20 Яндекс.Музыки"""
    from api.music_search import yandex
    
    # Получаем топ-20 чарта
    chart_tracks = await yandex.get_chart(limit=20)
    
    if not chart_tracks:
        await message.answer(
            "⚠️ <b>Не удалось загрузить чарт</b>\n\n"
            "Попробуй позже.",
            parse_mode='HTML'
        )
        return
    
    # Сохраняем в кэш для пользователя
    user_id = message.from_user.id
    search_results_cache[user_id] = chart_tracks
    
    # Формируем сообщение
    text = f"🎧 <b>Топ-20 Яндекс.Музыки</b>\n\n"
    text += "👇 <b>Выбери трек для скачивания:</b>"
    
    # Показываем первую страницу (5 треков)
    await message.answer(
        text,
        reply_markup=get_chart_keyboard(chart_tracks, page=0),
        parse_mode='HTML'
    )


@router.message(F.text == "📊 Статистика")
async def show_admin_stats(message: Message):
    """Показать статистику (только для админов)"""
    from config.settings import ADMIN_IDS
    
    # Проверяем права админа
    if message.from_user.id not in ADMIN_IDS and message.chat.id not in ADMIN_IDS:
        return  # Игнорируем если не админ
    
    if not router.db:
        await message.answer("⚠️ База данных недоступна")
        return
    
    try:
        # Получаем статистику из БД
        from database.db import async_session
        from database.models import User, DownloadHistory, Favorite
        from sqlalchemy import func, select
        
        async with async_session() as session:
            # Общее количество пользователей
            total_users = await session.scalar(select(func.count(User.id)))
            
            # Количество скачиваний
            total_downloads = await session.scalar(select(func.count(DownloadHistory.id)))
            
            # Количество избранных треков
            total_favorites = await session.scalar(select(func.count(Favorite.id)))
            
            # Активные пользователи (скачавшие хотя бы 1 трек)
            active_users = await session.scalar(
                select(func.count(func.distinct(DownloadHistory.user_id)))
            )
            
            # Топ-5 источников
            top_sources = await session.execute(
                select(
                    DownloadHistory.source,
                    func.count(DownloadHistory.id).label('count')
                )
                .group_by(DownloadHistory.source)
                .order_by(func.count(DownloadHistory.id).desc())
                .limit(5)
            )
            top_sources = top_sources.all()
        
        # Формируем сообщение
        text = "📊 <b>Статистика бота</b>\n\n"
        text += f"👥 <b>Всего пользователей:</b> {total_users or 0}\n"
        text += f"✅ <b>Активных:</b> {active_users or 0}\n\n"
        text += f"💾 <b>Скачиваний:</b> {total_downloads or 0}\n"
        text += f"❤️ <b>В избранном:</b> {total_favorites or 0}\n\n"
        
        if top_sources:
            text += "<b>📍 Популярные источники:</b>\n"
            source_emoji = {
                'deezer': '🔵',
                'yandex': '🟡',
                'lmusic': '🎵',
                'soundcloud': '🟠'
            }
            for source, count in top_sources:
                emoji = source_emoji.get(source, '⚪')
                text += f"{emoji} {source}: {count}\n"
        
        await message.answer(text, parse_mode='HTML')
    
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
        await message.answer("❌ Ошибка получения статистики")


@router.message(F.text)
async def search_handler(message: Message):
    """Поиск музыки по запросу - выбор источника"""
    query = message.text.strip()
    
    if len(query) < 2:
        await message.answer("❌ Запрос слишком короткий. Напиши хотя бы 2 символа.")
        return
    
    if len(query) > 200:
        await message.answer("❌ Запрос слишком длинный. Максимум 200 символов.")
        return
    
    # Создаём короткий ID для запроса
    query_id = hashlib.md5(query.encode()).hexdigest()[:8]
    query_cache[query_id] = query
    
    # Предлагаем выбрать источник
    await message.answer(
        f"🎵 <b>Поиск:</b> {query}\n\n"
        "📍 <b>Выбери источник:</b>",
        reply_markup=get_source_selection_keyboard(query_id),
        parse_mode='HTML'
    )


@router.callback_query(F.data.startswith("search_"))
async def handle_source_selection(callback: CallbackQuery):
    """Обработка выбора источника поиска"""
    data = callback.data
    
    # Парсим данные: search_SOURCE_QUERYID
    parts = data.split("_", 2)
    if len(parts) < 3:
        await callback.answer("❌ Ошибка", show_alert=True)
        return
    
    source = parts[1]  # deezer, yandex, soundcloud, all
    query_id = parts[2]   # ID запроса
    
    # Получаем реальный запрос из кэша
    query = query_cache.get(query_id)
    if not query:
        await callback.answer("❌ Запрос устарел. Начни поиск заново.", show_alert=True)
        return
    
    # Показываем что ищем
    source_names = {
        'deezer': '🔵 Deezer',
        'yandex': '🟡 Яндекс.Музыка',
        'soundcloud': '🎵 Music Original',
        'all': '🔍 Везде'
    }
    
    await callback.message.edit_text(
        f"🔍 Ищу в {source_names.get(source, 'источнике')}: <b>{query}</b>...",
        parse_mode='HTML'
    )
    
    # Ищем музыку
    results = await search_by_source(query, source)
    
    if not results:
        await callback.message.edit_text(
            f"😔 По запросу '<b>{query}</b>' ничего не найдено в {source_names.get(source, 'источнике')}.\n\n"
            "Попробуй изменить запрос или выбрать другой источник.",
            parse_mode='HTML'
        )
        return
    
    # Сохраняем результаты в кэш
    user_id = callback.from_user.id
    search_results_cache[user_id] = results
    
    # Формируем результаты
    results_text = f"🎵 <b>Найдено треков:</b> {len(results)}\n"
    results_text += f"📍 <b>Источник:</b> {source_names.get(source, 'неизвестен')}\n\n"
    results_text += "👇 <b>Выбери трек для скачивания:</b>"
    
    # Показываем результаты с кнопками
    await callback.message.edit_text(
        results_text,
        reply_markup=get_search_results_keyboard(results, page=0),
        parse_mode='HTML'
    )
    
    await callback.answer()

    
    await callback.answer()


@router.callback_query(F.data.startswith("download_"))
async def download_track(callback: CallbackQuery):
    """Скачивание трека"""
    track_id = callback.data.replace("download_", "")
    user_id = callback.from_user.id
    
    # Получаем результаты поиска из кэша
    results = search_results_cache.get(user_id, [])
    
    # Находим трек по ID
    track = None
    for t in results:
        if t['id'] == track_id:
            track = t
            break
    
    if not track:
        await callback.answer("❌ Трек не найден", show_alert=True)
        return
    
    # Показываем что скачиваем
    await callback.message.edit_text(
        f"⏬ <b>Скачиваю трек...</b>\n\n"
        f"🎵 <b>{track['artist']}</b> - {track['title']}\n"
        f"💿 {track['album']}\n\n"
        f"⏳ Ищу на YouTube/SoundCloud и скачиваю...\n"
        f"<i>Это может занять 10-30 секунд</i>",
        parse_mode='HTML'
    )
    
    await callback.answer()
    
    # Скачиваем трек
    try:
        # Определяем нужен ли приоритет SoundCloud
        prefer_soundcloud = track.get('source') == 'soundcloud'
        
        # Для lmusic.kz скачиваем напрямую
        if track.get('source') == 'lmusic':
            result = await downloader.search_and_download(
                artist=track['artist'],
                title=track['title'],
                source='lmusic',
                download_url=track.get('url')
            )
        else:
            # Для остальных источников - через YouTube
            result = await downloader.search_and_download(
                artist=track['artist'],
                title=track['title'],
                prefer_soundcloud=prefer_soundcloud
            )
        
        if not result or not os.path.exists(result['file_path']):
            await callback.message.edit_text(
                f"❌ <b>Не удалось скачать трек</b>\n\n"
                f"🎵 {track['artist']} - {track['title']}\n\n"
                f"Возможные причины:\n"
                f"• Трек не найден на YouTube\n"
                f"• Проблемы с загрузкой\n"
                f"• Трек защищён от скачивания\n\n"
                f"Попробуй другой трек или измени запрос.",
                parse_mode='HTML'
            )
            return
        
        # Отправляем файл
        audio_file = FSInputFile(result['file_path'])
        
        sent_message = await callback.message.answer_audio(
            audio=audio_file,
            title=track['title'],
            performer=track['artist'],
            caption=f"🎵 <b>{track['artist']}</b> - {track['title']}\n💿 {track['album']}\n\n@Music_good_bot",
            parse_mode='HTML',
            reply_markup=get_track_actions_keyboard(track['id'])
        )
        
        # Добавляем в историю
        if router.db:
            await router.db.add_download_history(
                user_id=user_id,
                track_title=track['title'],
                track_artist=track['artist'],
                source=track.get('source', 'unknown')
            )
        
        # Удаляем сообщение "Скачиваю..."
        await callback.message.delete()
        
        # Удаляем файл после отправки
        downloader.cleanup(result['file_path'])
        
    except Exception as e:
        print(f"❌ Ошибка при скачивании: {e}")
        await callback.message.edit_text(
            f"❌ <b>Ошибка при скачивании</b>\n\n"
            f"🎵 {track['artist']} - {track['title']}\n\n"
            f"Попробуй ещё раз или выбери другой трек.",
            parse_mode='HTML'
        )


@router.callback_query(F.data.startswith("page_"))
async def change_page(callback: CallbackQuery):
    """Переключение страниц результатов"""
    try:
        # Парсим данные
        page_data = callback.data.replace("page_", "")
        
        if page_data == "info":
            await callback.answer("ℹ️ Используй кнопки для навигации")
            return
        
        page = int(page_data)
        user_id = callback.from_user.id
        
        # Получаем результаты из кэша
        results = search_results_cache.get(user_id, [])
        
        if not results:
            await callback.answer("❌ Результаты поиска устарели. Начни поиск заново.", show_alert=True)
            return
        
        # Обновляем сообщение с новой страницей
        await callback.message.edit_reply_markup(
            reply_markup=get_search_results_keyboard(results, page=page)
        )
        
        await callback.answer(f"📄 Страница {page + 1}")
        
    except Exception as e:
        print(f"❌ Ошибка переключения страницы: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("favorite_add_"))
async def add_to_favorites(callback: CallbackQuery):
    """Добавить в избранное"""
    if not router.db:
        await callback.answer("⚠️ База данных недоступна", show_alert=True)
        return
    
    track_id = callback.data.replace("favorite_add_", "")
    user_id = callback.from_user.id
    
    # Получаем трек из кэша
    results = search_results_cache.get(user_id, [])
    track = None
    for t in results:
        if t['id'] == track_id:
            track = t
            break
    
    if not track:
        await callback.answer("❌ Трек не найден", show_alert=True)
        return
    
    # Добавляем в избранное
    added = await router.db.add_to_favorites(
        user_id=user_id,
        track_title=track['title'],
        track_artist=track['artist'],
        track_album=track.get('album'),
        source=track.get('source')
    )
    
    if added:
        await callback.answer("❤️ Добавлено в избранное!", show_alert=True)
    else:
        await callback.answer("ℹ️ Уже в избранном", show_alert=True)


@router.callback_query(F.data.startswith("chart_page_"))
async def change_chart_page(callback: CallbackQuery):
    """Переключение страниц чарта"""
    try:
        page_data = callback.data.replace("chart_page_", "")
        
        if page_data == "info":
            await callback.answer("ℹ️ Используй кнопки для навигации")
            return
        
        page = int(page_data)
        user_id = callback.from_user.id
        
        # Получаем треки из кэша
        tracks = search_results_cache.get(user_id, [])
        
        if not tracks:
            await callback.answer("❌ Чарт устарел. Открой рекомендации заново.", show_alert=True)
            return
        
        # Обновляем сообщение с новой страницей
        from bot.keyboards import get_chart_keyboard
        await callback.message.edit_reply_markup(
            reply_markup=get_chart_keyboard(tracks, page=page)
        )
        
        await callback.answer(f"📄 Страница {page + 1}")
        
    except Exception as e:
        print(f"❌ Ошибка переключения страницы чарта: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("share_"))
async def share_track(callback: CallbackQuery):
    """Поделиться треком"""
    track_id = callback.data.replace("share_", "")
    user_id = callback.from_user.id
    
    # Получаем трек из кэша
    results = search_results_cache.get(user_id, [])
    track = None
    for t in results:
        if t['id'] == track_id:
            track = t
            break
    
    if not track:
        await callback.answer("❌ Трек не найден", show_alert=True)
        return
    
    # Формируем текст для шаринга
    share_text = f"🎵 {track['artist']} - {track['title']}\n\n"
    share_text += f"Найдено через @Music_good_bot\n"
    share_text += f"Попробуй сам: t.me/Music_good_bot"
    
    await callback.message.answer(
        f"📤 <b>Поделиться треком:</b>\n\n{share_text}\n\n"
        "<i>Скопируй текст выше и отправь друзьям!</i>",
        parse_mode='HTML'
    )
    
    await callback.answer("✅ Текст для шаринга отправлен")
