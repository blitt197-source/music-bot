"""
Главный файл Telegram бота
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import BOT_TOKEN, PROXY_URL, DATABASE_URL
from bot.handlers import router
from database.db import Database

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная БД
db = None


async def main():
    """Запуск бота"""
    global db
    
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не найден! Создай файл .env и добавь токен")
        return
    
    # Инициализируем БД
    db = Database(DATABASE_URL)
    await db.init_db()
    
    # Создаём бота и диспетчер
    if PROXY_URL:
        from aiogram.client.session.aiohttp import AiohttpSession
        session = AiohttpSession(proxy=PROXY_URL)
        bot = Bot(token=BOT_TOKEN, session=session)
        logger.info(f"🔒 Используется прокси: {PROXY_URL}")
    else:
        bot = Bot(token=BOT_TOKEN)
    
    dp = Dispatcher()
    
    # Передаём БД в роутер
    router.db = db
    
    # Подключаем обработчики
    dp.include_router(router)
    
    logger.info("🚀 Бот запущен!")
    
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен")
