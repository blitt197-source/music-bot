"""
Парсинг lmusic.kz для скачивания музыки
"""
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import re


class LMusicParser:
    """Парсер lmusic.kz"""
    
    def __init__(self):
        """Инициализация парсера"""
        self.base_url = 'https://lmusic.kz'
        self.enabled = True
        print("✅ LMusic.kz парсер подключен (Music Original)")
    
    async def search(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Поиск треков на lmusic.kz
        
        Args:
            query: поисковый запрос
            limit: максимальное количество результатов
        
        Returns:
            Список треков
        """
        if not self.enabled:
            return []
        
        try:
            print(f"🔍 Ищу на lmusic.kz: {query}")
            
            tracks = await self._search_query(query, limit)
            
            # Если найдено мало треков, попробуем поискать по первому слову
            if len(tracks) < 5 and ' ' in query:
                first_word = query.split()[0]
                print(f"🔍 Мало результатов, ищу по: {first_word}")
                additional_tracks = await self._search_query(first_word, limit)
                
                # Добавляем только уникальные треки
                existing_ids = {t['id'] for t in tracks}
                for track in additional_tracks:
                    if track['id'] not in existing_ids:
                        tracks.append(track)
                        existing_ids.add(track['id'])
                        if len(tracks) >= limit:
                            break
            
            print(f"✅ Найдено {len(tracks)} треков на lmusic.kz")
            return tracks[:limit]
        
        except Exception as e:
            print(f"❌ Ошибка поиска на lmusic.kz: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _search_query(self, query: str, limit: int) -> List[Dict]:
        """Внутренний метод для поиска по одному запросу"""
        # Формируем URL поиска
        search_url = f"{self.base_url}/search/{query}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                if response.status != 200:
                    print(f"❌ lmusic.kz вернул статус {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                tracks = []
                
                # Ищем все треки в результатах поиска
                # Структура: <a href="/mp3/artist-title/ID">Название</a>
                track_links = soup.find_all('a', href=re.compile(r'/mp3/[^/]+/\d+'))
                
                seen_ids = set()
                
                for link in track_links[:limit]:
                    try:
                        href = link.get('href', '')
                        
                        # Извлекаем ID трека из URL
                        match = re.search(r'/mp3/([^/]+)/(\d+)', href)
                        if not match:
                            continue
                        
                        track_slug = match.group(1)
                        track_id = match.group(2)
                        
                        # Проверяем дубликаты
                        if track_id in seen_ids:
                            continue
                        seen_ids.add(track_id)
                        
                        # Получаем название трека
                        title_text = link.get_text(strip=True)
                        
                        # Ищем исполнителя - поднимаемся на 1 уровень выше
                        parent = link.find_parent()
                        if parent:
                            parent = parent.find_parent()  # Поднимаемся ещё на 1 уровень
                        
                        # Теперь ищем всех исполнителей
                        artist_links = parent.find_all('a', href=re.compile(r'/artist/')) if parent else []
                        
                        if artist_links:
                            # Собираем всех исполнителей через запятую
                            artists = [a.get_text(strip=True) for a in artist_links]
                            artist = ', '.join(artists)
                        else:
                            artist = 'Неизвестный исполнитель'
                        
                        # Формируем URL для скачивания
                        download_url = f"{self.base_url}/api/download/{track_id}"
                        
                        track_info = {
                            'id': f"lmusic_{track_id}",
                            'title': title_text,
                            'artist': artist,
                            'album': 'Music Original',
                            'duration': 0,
                            'url': download_url,
                            'preview_url': None,
                            'cover': None,
                            'source': 'lmusic'
                        }
                        tracks.append(track_info)
                        
                        if len(tracks) >= limit:
                            break
                    
                    except Exception as e:
                        continue
                
                return tracks
    
    async def download_direct(self, url: str, output_path: str) -> bool:
        """
        Скачать файл по прямой ссылке
        
        Args:
            url: ссылка на MP3
            output_path: путь для сохранения
        
        Returns:
            True если успешно
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            f.write(await response.read())
                        return True
            return False
        except Exception as e:
            print(f"❌ Ошибка скачивания: {e}")
            return False
