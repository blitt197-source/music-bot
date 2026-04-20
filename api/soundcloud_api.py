"""
SoundCloud API для поиска музыки
"""
import aiohttp
from typing import List, Dict


class SoundCloudAPI:
    """Класс для работы с SoundCloud"""
    
    def __init__(self):
        """Инициализация SoundCloud API"""
        # Используем публичный поиск через веб-версию
        self.enabled = True
        print("✅ SoundCloud подключен")
    
    async def search(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Поиск треков в SoundCloud
        
        Args:
            query: поисковый запрос
            limit: максимальное количество результатов
        
        Returns:
            Список треков
        """
        if not self.enabled:
            return []
        
        try:
            print(f"🔍 Ищу в SoundCloud: {query}")
            
            # Используем поиск через yt-dlp
            # SoundCloud треки будут в формате soundcloud.com/...
            # Пока возвращаем пустой список, поиск будет через yt-dlp при скачивании
            
            # TODO: Можно добавить парсинг поиска SoundCloud
            # Но для начала достаточно скачивания
            
            print("⚠️ Поиск SoundCloud пока не реализован, но скачивание работает!")
            return []
        
        except Exception as e:
            print(f"❌ Ошибка поиска в SoundCloud: {e}")
            return []
