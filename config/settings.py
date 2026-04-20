"""
Настройки бота
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')
PROXY_URL = os.getenv('PROXY_URL')

# База данных
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./music_bot.db')

# Пути
DOWNLOADS_DIR = 'downloads'
MUSIC_DIR = 'music'

# Создаём папки если их нет
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)

# Лимиты
MAX_SEARCH_RESULTS = 10
RESULTS_PER_PAGE = 10

# Админы (ID пользователей или чатов)
ADMIN_IDS = [
    -1003911154683,  # Твой ID
]
