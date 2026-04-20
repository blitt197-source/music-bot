"""
API для поиска музыки
"""
import asyncio
from typing import List, Dict
from api.deezer_api import DeezerAPI
from api.yandex_api import YandexMusicAPI
from api.soundcloud_api import SoundCloudAPI
from api.mp3party_parser import LMusicParser


# Глобальные экземпляры API
deezer = DeezerAPI()
yandex = YandexMusicAPI()
soundcloud = SoundCloudAPI()
lmusic = LMusicParser()


async def search_by_source(query: str, source: str = 'all', limit: int = 50) -> List[Dict]:
    """
    Поиск музыки по запросу в выбранном источнике
    
    Args:
        query: поисковый запрос
        source: источник ('deezer', 'yandex', 'soundcloud', 'all')
        limit: максимальное количество результатов
    
    Returns:
        Список треков с информацией
    """
    results = []
    
    if source == 'deezer':
        # Только Deezer
        if deezer.enabled:
            results = await deezer.search(query, limit=limit)
        else:
            print("⚠️ Deezer не настроен")
    
    elif source == 'yandex':
        # Только Яндекс.Музыка
        results = await yandex.search(query, limit=limit)
    
    elif source == 'soundcloud':
        # Music Original вместо SoundCloud
        print("🎵 Music Original: поиск оригиналов")
        results = await lmusic.search(query, limit=limit)
    
    elif source == 'all':
        # Все источники
        tasks = []
        
        if deezer.enabled:
            tasks.append(deezer.search(query, limit=limit // 3))
        
        tasks.append(yandex.search(query, limit=limit // 3))
        
        if tasks:
            search_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in search_results:
                if isinstance(result, list):
                    results.extend(result)
    
    # Если ничего не найдено, возвращаем тестовые данные
    if not results:
        print(f"⚠️ Ничего не найдено в {source}, используем тестовые данные")
        results = _get_mock_results(query, limit)
    
    # Убираем дубликаты по названию + исполнитель
    unique_results = []
    seen = set()
    
    for track in results:
        key = f"{track['artist'].lower()}_{track['title'].lower()}"
        if key not in seen:
            seen.add(key)
            unique_results.append(track)
    
    return unique_results[:limit]


def _get_soundcloud_mock(query: str, limit: int) -> List[Dict]:
    """Заглушка для Music Original - если парсер не сработал"""
    return [{
        'id': f'lmusic_fallback',
        'title': f'{query}',
        'artist': '🎵 Music Original',
        'album': 'Поиск через YouTube',
        'duration': 0,
        'url': None,
        'preview_url': None,
        'cover': None,
        'source': 'lmusic'
    }]


async def search_music(query: str, limit: int = 50) -> List[Dict]:
    """
    Поиск музыки по запросу (комбинированный поиск)
    Устаревшая функция, используй search_by_source
    """
    return await search_by_source(query, source='all', limit=limit)


def _get_mock_results(query: str, limit: int) -> List[Dict]:
    """Тестовые данные если API не работают"""
    mock_results = []
    
    for i in range(1, min(limit, 20) + 1):
        mock_results.append({
            'id': f'track_{i}',
            'title': f'{query} - Трек {i}',
            'artist': f'Исполнитель {i}',
            'album': f'Альбом {i}',
            'duration': 180 + i * 10,
            'url': None,
            'preview_url': None,
            'cover': None,
            'source': 'mock'
        })
    
    return mock_results


async def search_deezer(query: str, limit: int = 50) -> List[Dict]:
    """
    Поиск через Deezer API (бесплатный, без ключа)
    
    Args:
        query: поисковый запрос
        limit: максимальное количество результатов
    """
    url = 'https://api.deezer.com/search'
    params = {
        'q': query,
        'limit': limit
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = []
                    for track in data.get('data', []):
                        results.append({
                            'id': str(track['id']),
                            'title': track['title'],
                            'artist': track['artist']['name'],
                            'album': track['album']['title'],
                            'duration': track['duration'],
                            'url': track['link'],
                            'preview_url': track.get('preview'),
                            'cover': track['album'].get('cover_medium'),
                        })
                    
                    return results
    except Exception as e:
        print(f"Ошибка поиска в Deezer: {e}")
    
    return []


async def get_track_info(track_id: str) -> Dict:
    """
    Получить информацию о треке
    
    Args:
        track_id: ID трека
    
    Returns:
        Информация о треке
    """
    # TODO: Реализовать получение информации
    return {
        'id': track_id,
        'title': 'Название трека',
        'artist': 'Исполнитель',
        'album': 'Альбом',
        'duration': 180,
    }
