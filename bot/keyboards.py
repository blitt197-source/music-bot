"""
Клавиатуры для бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu(is_admin: bool = False):
    """
    Главное меню бота
    
    Args:
        is_admin: является ли пользователь админом
    """
    keyboard_buttons = [
        [
            KeyboardButton(text="❤️ Избранное"),
            KeyboardButton(text="🎵 Рекомендации дня")
        ]
    ]
    
    # Для админов добавляем кнопку статистики
    if is_admin:
        keyboard_buttons.append([
            KeyboardButton(text="📊 Статистика")
        ])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard_buttons,
        resize_keyboard=True
    )
    return keyboard


def get_source_selection_keyboard(query_id: str):
    """
    Клавиатура выбора источника поиска
    
    Args:
        query_id: короткий ID запроса (не сам запрос!)
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔵 Deezer",
                    callback_data=f"search_deezer_{query_id}"
                ),
                InlineKeyboardButton(
                    text="🟡 Яндекс.Музыка",
                    callback_data=f"search_yandex_{query_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎵 Music Original",
                    callback_data=f"search_soundcloud_{query_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Искать везде",
                    callback_data=f"search_all_{query_id}"
                )
            ]
        ]
    )
    return keyboard


def get_search_results_keyboard(results, page=0, per_page=10):
    """
    Клавиатура с результатами поиска
    
    Args:
        results: список треков
        page: текущая страница
        per_page: треков на странице
    """
    buttons = []
    
    # Вычисляем диапазон треков для текущей страницы
    start = page * per_page
    end = start + per_page
    page_results = results[start:end]
    
    # Кнопки для каждого трека
    for idx, track in enumerate(page_results, start=start + 1):
        # Эмодзи источника
        source_emoji = {
            'deezer': '🔵',
            'yandex': '🟡',
            'soundcloud': '🟠',
            'lmusic': '🎵',
            'mock': '⚪'
        }.get(track.get('source', 'mock'), '⚪')
        
        track_text = f"{source_emoji} {idx}. {track['artist']} — {track['title']}"
        buttons.append([
            InlineKeyboardButton(
                text=track_text,
                callback_data=f"download_{track['id']}"
            )
        ])
    
    # Кнопки навигации
    nav_buttons = []
    
    # Кнопка "Назад"
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"page_{page - 1}")
        )
    
    # Информация о странице
    total_pages = (len(results) + per_page - 1) // per_page
    nav_buttons.append(
        InlineKeyboardButton(
            text=f"📄 {page + 1}/{total_pages}",
            callback_data="page_info"
        )
    )
    
    # Кнопка "Вперёд"
    if end < len(results):
        nav_buttons.append(
            InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"page_{page + 1}")
        )
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard



def get_favorites_keyboard(favorites, page=0, per_page=10):
    """
    Клавиатура с избранным
    
    Args:
        favorites: список избранных треков
        page: текущая страница
        per_page: треков на странице
    """
    buttons = []
    
    # Вычисляем диапазон
    start = page * per_page
    end = start + per_page
    page_favorites = favorites[start:end]
    
    # Кнопки для каждого трека
    for idx, fav in enumerate(page_favorites, start=start + 1):
        track_text = f"🎵 {idx}. {fav.track_artist} — {fav.track_title}"
        buttons.append([
            InlineKeyboardButton(
                text=track_text,
                callback_data=f"fav_download_{fav.id}"
            )
        ])
    
    # Кнопки навигации
    nav_buttons = []
    
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"fav_page_{page - 1}")
        )
    
    total_pages = (len(favorites) + per_page - 1) // per_page
    nav_buttons.append(
        InlineKeyboardButton(
            text=f"📄 {page + 1}/{total_pages}",
            callback_data="fav_page_info"
        )
    )
    
    if end < len(favorites):
        nav_buttons.append(
            InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"fav_page_{page + 1}")
        )
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_track_actions_keyboard(track_id: str):
    """
    Клавиатура с действиями для трека
    
    Args:
        track_id: ID трека
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❤️ В избранное",
                    callback_data=f"favorite_add_{track_id}"
                ),
                InlineKeyboardButton(
                    text="📤 Поделиться",
                    callback_data=f"share_{track_id}"
                )
            ]
        ]
    )
    return keyboard


def get_chart_keyboard(tracks, page=0, per_page=5):
    """
    Клавиатура для топ-чарта (по 5 треков на странице)
    
    Args:
        tracks: список треков
        page: текущая страница
        per_page: треков на странице
    """
    buttons = []
    
    # Вычисляем диапазон треков для текущей страницы
    start = page * per_page
    end = start + per_page
    page_tracks = tracks[start:end]
    
    # Кнопки для каждого трека
    for idx, track in enumerate(page_tracks, start=start + 1):
        track_text = f"🟡 {idx}. {track['artist']} — {track['title']}"
        buttons.append([
            InlineKeyboardButton(
                text=track_text,
                callback_data=f"download_{track['id']}"
            )
        ])
    
    # Кнопки навигации
    nav_buttons = []
    
    # Кнопка "Назад"
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"chart_page_{page - 1}")
        )
    
    # Информация о странице
    total_pages = (len(tracks) + per_page - 1) // per_page
    nav_buttons.append(
        InlineKeyboardButton(
            text=f"📄 {page + 1}/{total_pages}",
            callback_data="chart_page_info"
        )
    )
    
    # Кнопка "Вперёд"
    if end < len(tracks):
        nav_buttons.append(
            InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"chart_page_{page + 1}")
        )
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

