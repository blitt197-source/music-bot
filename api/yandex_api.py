"""
Яндекс.Музыка API для поиска музыки
"""
from yandex_music import ClientAsync
from typing import List, Dict
import os


class YandexMusicAPI:
    """Класс для работы с Яндекс.Музыка API"""
    
    def __init__(self, token: str = None):
        """
        Инициализация Яндекс.Музыка API
        
        Args:
            token: Токен Яндекс.Музыки (опционально)
        """
        self.token = token or os.getenv('YANDEX_MUSIC_TOKEN')
        self.client = None
        self.enabled = False
    
    async def init(self):
        """Асинхронная инициализация клиента"""
        try:
            if self.token:
                self.client = await ClientAsync(self.token).init()
            else:
                # Без токена - публичный доступ (ограниченный)
                self.client = await ClientAsync().init()
            
            self.enabled = True
            print("✅ Яндекс.Музыка подключена")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации Яндекс.Музыки: {e}")
            self.enabled = False
    
    async def search(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Поиск треков в Яндекс.Музыке
        
        Args:
            query: поисковый запрос
            limit: максимальное количество результатов
        
        Returns:
            Список треков
        """
        if not self.enabled or not self.client:
            await self.init()
            if not self.enabled:
                return []
        
        try:
            search_result = await self.client.search(query, type_='track')
            
            if not search_result or not search_result.tracks:
                return []
            
            tracks = []
            for track in search_result.tracks.results[:limit]:
                # Получаем исполнителей
                artists = ', '.join([artist.name for artist in track.artists])
                
                # Получаем обложку
                cover_url = None
                if track.cover_uri:
                    cover_url = f"https://{track.cover_uri.replace('%%', '400x400')}"
                
                track_info = {
                    'id': f"yandex_{track.id}",
                    'title': track.title,
                    'artist': artists,
                    'album': track.albums[0].title if track.albums else 'Unknown',
                    'duration': track.duration_ms // 1000 if track.duration_ms else 0,
                    'url': f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}" if track.albums else None,
                    'preview_url': None,  # Яндекс не даёт прямые ссылки без авторизации
                    'cover': cover_url,
                    'source': 'yandex'
                }
                tracks.append(track_info)
            
            return tracks
        
        except Exception as e:
            print(f"Ошибка поиска в Яндекс.Музыке: {e}")
            return []
    
    async def get_track_info(self, track_id: str) -> Dict:
        """
        Получить информацию о треке
        
        Args:
            track_id: ID трека в Яндекс.Музыке
        
        Returns:
            Информация о треке
        """
        if not self.enabled or not self.client:
            return {}
        
        try:
            track = await self.client.tracks([track_id])
            if not track:
                return {}
            
            track = track[0]
            artists = ', '.join([artist.name for artist in track.artists])
            
            cover_url = None
            if track.cover_uri:
                cover_url = f"https://{track.cover_uri.replace('%%', '400x400')}"
            
            return {
                'id': f"yandex_{track.id}",
                'title': track.title,
                'artist': artists,
                'album': track.albums[0].title if track.albums else 'Unknown',
                'duration': track.duration_ms // 1000 if track.duration_ms else 0,
                'url': f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}" if track.albums else None,
                'cover': cover_url,
                'source': 'yandex'
            }
        except Exception as e:
            print(f"Ошибка получения трека: {e}")
            return {}
    
    async def get_chart(self, limit: int = 20) -> List[Dict]:
        """
        Получить топ чарт Яндекс.Музыки
        
        Args:
            limit: количество треков
        
        Returns:
            Список треков из чарта
        """
        if not self.enabled or not self.client:
            await self.init()
            if not self.enabled:
                return []
        
        try:
            # Получаем чарт России
            chart = await self.client.chart('russia')
            
            if not chart or not chart.chart:
                return []
            
            tracks = []
            for position in chart.chart.tracks[:limit]:
                track = position.track
                
                # Получаем исполнителей
                artists = ', '.join([artist.name for artist in track.artists])
                
                # Получаем обложку
                cover_url = None
                if track.cover_uri:
                    cover_url = f"https://{track.cover_uri.replace('%%', '400x400')}"
                
                track_info = {
                    'id': f"yandex_{track.id}",
                    'title': track.title,
                    'artist': artists,
                    'album': track.albums[0].title if track.albums else 'Unknown',
                    'duration': track.duration_ms // 1000 if track.duration_ms else 0,
                    'url': f"https://music.yandex.ru/album/{track.albums[0].id}/track/{track.id}" if track.albums else None,
                    'preview_url': None,
                    'cover': cover_url,
                    'source': 'yandex'
                }
                tracks.append(track_info)
            
            return tracks
        
        except Exception as e:
            print(f"❌ Ошибка получения чарта: {e}")
            return []
    
    async def close(self):
        """Закрыть соединение"""
        if self.client:
            await self.client.close()
