"""
Spotify API для поиска музыки
"""
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List, Dict
import os


class SpotifyAPI:
    """Класс для работы со Spotify API"""
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        """
        Инициализация Spotify API
        
        Args:
            client_id: Spotify Client ID
            client_secret: Spotify Client Secret
        """
        self.client_id = client_id or os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if self.client_id and self.client_secret:
            try:
                print(f"🔑 Инициализирую Spotify API...")
                print(f"Client ID: {self.client_id[:10]}...")
                auth_manager = SpotifyClientCredentials(
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
                self.enabled = True
                print("✅ Spotify API подключен!")
            except Exception as e:
                print(f"⚠️ Ошибка инициализации Spotify: {e}")
                import traceback
                traceback.print_exc()
                self.enabled = False
        else:
            print("⚠️ Spotify API ключи не найдены в .env")
            print(f"Client ID: {self.client_id}")
            print(f"Client Secret: {self.client_secret}")
            self.enabled = False
    
    async def search(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Поиск треков в Spotify
        
        Args:
            query: поисковый запрос
            limit: максимальное количество результатов
        
        Returns:
            Список треков
        """
        if not self.enabled:
            print("⚠️ Spotify не включен")
            return []
        
        try:
            print(f"🔍 Ищу в Spotify: {query}")
            results = self.sp.search(q=query, type='track', limit=limit)
            tracks = []
            
            for item in results['tracks']['items']:
                # Получаем исполнителей
                artists = ', '.join([artist['name'] for artist in item['artists']])
                
                track_info = {
                    'id': f"spotify_{item['id']}",
                    'title': item['name'],
                    'artist': artists,
                    'album': item['album']['name'],
                    'duration': item['duration_ms'] // 1000,  # в секундах
                    'url': item['external_urls']['spotify'],
                    'preview_url': item.get('preview_url'),
                    'cover': item['album']['images'][0]['url'] if item['album']['images'] else None,
                    'source': 'spotify'
                }
                tracks.append(track_info)
            
            print(f"✅ Найдено {len(tracks)} треков в Spotify")
            return tracks
        
        except Exception as e:
            print(f"❌ Ошибка поиска в Spotify: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_track_info(self, track_id: str) -> Dict:
        """
        Получить информацию о треке
        
        Args:
            track_id: ID трека в Spotify
        
        Returns:
            Информация о треке
        """
        if not self.enabled:
            return {}
        
        try:
            track = self.sp.track(track_id)
            artists = ', '.join([artist['name'] for artist in track['artists']])
            
            return {
                'id': f"spotify_{track['id']}",
                'title': track['name'],
                'artist': artists,
                'album': track['album']['name'],
                'duration': track['duration_ms'] // 1000,
                'url': track['external_urls']['spotify'],
                'preview_url': track.get('preview_url'),
                'cover': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'source': 'spotify'
            }
        except Exception as e:
            print(f"Ошибка получения трека: {e}")
            return {}
