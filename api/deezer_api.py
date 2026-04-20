"""
Deezer API для поиска музыки (бесплатный, без ключей)
"""
import aiohttp
from typing import List, Dict


class DeezerAPI:
    """Класс для работы с Deezer API"""
    
    def __init__(self):
        """Инициализация Deezer API"""
        self.base_url = 'https://api.deezer.com'
        self.enabled = True
        print("✅ Deezer API подключен (бесплатный)")
    
    async def search(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Поиск треков в Deezer
        
        Args:
            query: поисковый запрос
            limit: максимальное количество результатов
        
        Returns:
            Список треков
        """
        if not self.enabled:
            return []
        
        try:
            print(f"🔍 Ищу в Deezer: {query}")
            
            url = f'{self.base_url}/search'
            params = {
                'q': query,
                'limit': limit
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        print(f"❌ Deezer вернул статус {response.status}")
                        return []
                    
                    data = await response.json()
                    
                    if 'data' not in data:
                        print("❌ Нет данных в ответе Deezer")
                        return []
                    
                    tracks = []
                    for track in data['data']:
                        # Получаем исполнителя
                        artist = track.get('artist', {}).get('name', 'Unknown')
                        
                        # Получаем обложку
                        cover = track.get('album', {}).get('cover_medium')
                        
                        track_info = {
                            'id': f"deezer_{track['id']}",
                            'title': track.get('title', 'Unknown'),
                            'artist': artist,
                            'album': track.get('album', {}).get('title', 'Unknown'),
                            'duration': track.get('duration', 0),
                            'url': track.get('link'),
                            'preview_url': track.get('preview'),
                            'cover': cover,
                            'source': 'deezer'
                        }
                        tracks.append(track_info)
                    
                    print(f"✅ Найдено {len(tracks)} треков в Deezer")
                    return tracks
        
        except Exception as e:
            print(f"❌ Ошибка поиска в Deezer: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def get_track_info(self, track_id: str) -> Dict:
        """
        Получить информацию о треке
        
        Args:
            track_id: ID трека в Deezer
        
        Returns:
            Информация о треке
        """
        try:
            url = f'{self.base_url}/track/{track_id}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return {}
                    
                    track = await response.json()
                    
                    return {
                        'id': f"deezer_{track['id']}",
                        'title': track.get('title', 'Unknown'),
                        'artist': track.get('artist', {}).get('name', 'Unknown'),
                        'album': track.get('album', {}).get('title', 'Unknown'),
                        'duration': track.get('duration', 0),
                        'url': track.get('link'),
                        'preview_url': track.get('preview'),
                        'cover': track.get('album', {}).get('cover_medium'),
                        'source': 'deezer'
                    }
        except Exception as e:
            print(f"❌ Ошибка получения трека из Deezer: {e}")
            return {}
