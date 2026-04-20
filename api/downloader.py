"""
Скачивание музыки через YouTube
"""
import os
import asyncio
from typing import Dict, Optional
import yt_dlp
import ssl
import certifi


class MusicDownloader:
    """Класс для скачивания музыки"""
    
    def __init__(self, download_dir: str = 'downloads', proxy: str = None):
        """
        Инициализация загрузчика
        
        Args:
            download_dir: папка для скачивания
            proxy: прокси сервер (если нужен)
        """
        self.download_dir = download_dir
        self.proxy = proxy or os.getenv('PROXY_URL')
        os.makedirs(download_dir, exist_ok=True)
    
    async def search_and_download(self, artist: str, title: str, prefer_soundcloud: bool = False, source: str = None, download_url: str = None) -> Optional[Dict]:
        """
        Поиск и скачивание трека с YouTube/SoundCloud или напрямую с lmusic.kz
        
        Args:
            artist: исполнитель
            title: название трека
            prefer_soundcloud: приоритет SoundCloud (если True)
            source: источник трека ('lmusic' для прямого скачивания)
            download_url: прямая ссылка для скачивания (для lmusic.kz)
        
        Returns:
            Информация о скачанном файле или None
        """
        # Если это lmusic.kz - скачиваем напрямую
        if source == 'lmusic' and download_url:
            print(f"📥 Скачиваю напрямую с lmusic.kz: {artist} - {title}")
            return await self._download_direct_lmusic(download_url, artist, title)
        
        # Убираем служебные слова
        artist = artist.replace('SoundCloud', '').replace('Поиск в SoundCloud', '').replace('🟠', '').strip()
        
        # Пробуем разные варианты поискового запроса
        if prefer_soundcloud:
            # Приоритет SoundCloud - для источника 🟠 SoundCloud
            queries = [
                f"scsearch1:{artist} {title} -slowed -reverb -remix -cover -sped",
                f"{artist} {title} soundcloud -slowed -reverb -remix",
                f"{artist} {title} official audio -slowed -reverb -remix -cover -nightcore",
                f"{artist} {title} explicit -slowed -reverb -remix",
                f"{artist} {title} uncensored -slowed -reverb",
                f"{artist} {title} original -slowed -reverb -remix",
                f"{artist} {title} official audio",
                f"{artist} {title} audio",
                f"{artist} {title}",
            ]
        else:
            # Обычный поиск - для Deezer/Яндекс (только YouTube)
            queries = [
                f"{artist} {title} official audio -slowed -reverb -remix -cover -nightcore",
                f"{artist} {title} explicit -slowed -reverb -remix",
                f"{artist} {title} uncensored -slowed -reverb",
                f"{artist} {title} original -slowed -reverb -remix",
                f"{artist} {title} official audio",
                f"{artist} {title} audio",
                f"{artist} {title}",
            ]
        
        for query in queries:
            try:
                print(f"🔍 Пробую запрос: {query}")
                
                # Настройки yt-dlp (без конвертации, если FFmpeg не найден)
                ydl_opts = {
                    'format': 'bestaudio[ext=m4a]/bestaudio/best',  # Предпочитаем m4a
                    'outtmpl': os.path.join(self.download_dir, '%(id)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                    'default_search': 'ytsearch1',
                    'nocheckcertificate': True,
                    'ignoreerrors': False,
                    'no_color': True,
                    'source_address': '0.0.0.0',
                    'socket_timeout': 30,
                    'retries': 3,
                    'legacy_server_connect': True,
                }
                
                # Пробуем найти FFmpeg
                ffmpeg_path = self._find_ffmpeg()
                if ffmpeg_path:
                    print(f"✅ FFmpeg найден: {ffmpeg_path}")
                    ydl_opts['ffmpeg_location'] = ffmpeg_path
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                else:
                    print("⚠️ FFmpeg не найден, скачиваю без конвертации")
                
                # Добавляем прокси если есть
                if self.proxy:
                    ydl_opts['proxy'] = self.proxy
                    print(f"🔒 Использую прокси для YouTube: {self.proxy}")
                
                # Запускаем в отдельном потоке (yt-dlp синхронный)
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._download_sync,
                    query,
                    ydl_opts
                )
                
                if result:
                    print(f"✅ Успешно скачано с запросом: {query}")
                    return result
                else:
                    print(f"⚠️ Не удалось с запросом: {query}, пробую следующий...")
            
            except Exception as e:
                print(f"❌ Ошибка с запросом '{query}': {e}")
                continue
        
        print("❌ Не удалось скачать ни с одним запросом")
        return None
    
    def _download_sync(self, query: str, ydl_opts: dict) -> Optional[Dict]:
        """
        Синхронное скачивание (для запуска в executor)
        
        Args:
            query: поисковый запрос
            ydl_opts: настройки yt-dlp
        
        Returns:
            Информация о файле
        """
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Ищем и скачиваем
                print(f"🔍 Ищу на YouTube: {query}")
                info = ydl.extract_info(query, download=True)
                
                if not info:
                    print("❌ Ничего не найдено на YouTube")
                    return None
                
                # Если это результат поиска, берём первый элемент
                if 'entries' in info:
                    if not info['entries']:
                        print("❌ Пустой список результатов")
                        return None
                    info = info['entries'][0]
                
                # Получаем информацию о скачанном файле
                video_id = info['id']
                
                # Ищем скачанный файл (может быть .mp3, .m4a, .webm и т.д.)
                possible_extensions = ['mp3', 'm4a', 'webm', 'opus', 'ogg']
                file_path = None
                
                for ext in possible_extensions:
                    test_path = os.path.join(self.download_dir, f"{video_id}.{ext}")
                    if os.path.exists(test_path):
                        file_path = test_path
                        break
                
                if not file_path:
                    print(f"❌ Файл не найден для video_id: {video_id}")
                    return None
                
                print(f"✅ Скачано: {file_path}")
                
                return {
                    'file_path': file_path,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'artist': info.get('artist', 'Unknown'),
                    'thumbnail': info.get('thumbnail'),
                }
        
        except Exception as e:
            print(f"❌ Ошибка в _download_sync: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def download_by_url(self, url: str) -> Optional[Dict]:
        """
        Скачивание по прямой ссылке YouTube
        
        Args:
            url: ссылка на YouTube видео
        
        Returns:
            Информация о скачанном файле
        """
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.download_dir, '%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'no_warnings': True,
            }
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._download_sync,
                url,
                ydl_opts
            )
            
            return result
        
        except Exception as e:
            print(f"❌ Ошибка скачивания по URL: {e}")
            return None
    
    def cleanup(self, file_path: str):
        """
        Удалить скачанный файл
        
        Args:
            file_path: путь к файлу
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Удалён файл: {file_path}")
        except Exception as e:
            print(f"⚠️ Ошибка удаления файла: {e}")

    
    def _find_ffmpeg(self) -> Optional[str]:
        """
        Поиск FFmpeg в системе
        
        Returns:
            Путь к FFmpeg или None
        """
        import shutil
        
        # Пробуем найти через shutil
        ffmpeg = shutil.which('ffmpeg')
        if ffmpeg:
            return os.path.dirname(ffmpeg)
        
        # Пробуем стандартные пути Chocolatey и другие
        possible_paths = [
            r'C:\ProgramData\chocolatey\bin',
            r'C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin',
            r'C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg-7.1-essentials_build\bin',
            r'C:\ffmpeg\bin',
        ]
        
        for path in possible_paths:
            ffmpeg_exe = os.path.join(path, 'ffmpeg.exe')
            if os.path.exists(ffmpeg_exe):
                print(f"✅ Нашёл FFmpeg: {ffmpeg_exe}")
                return path
        
        print("⚠️ FFmpeg не найден в стандартных путях")
        return None
    
    async def _download_direct_lmusic(self, url: str, artist: str, title: str) -> Optional[Dict]:
        """
        Прямое скачивание с lmusic.kz
        
        Args:
            url: URL для скачивания
            artist: исполнитель
            title: название
        
        Returns:
            Информация о файле
        """
        import aiohttp
        import hashlib
        
        try:
            # Генерируем имя файла
            file_id = hashlib.md5(f"{artist}_{title}".encode()).hexdigest()[:10]
            file_path = os.path.join(self.download_dir, f"{file_id}.mp3")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://lmusic.kz/'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=60)) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            f.write(await response.read())
                        
                        print(f"✅ Скачано с lmusic.kz: {file_path}")
                        
                        return {
                            'file_path': file_path,
                            'title': title,
                            'duration': 0,
                            'artist': artist,
                            'thumbnail': None,
                        }
                    else:
                        print(f"❌ lmusic.kz вернул статус {response.status}")
                        return None
        
        except Exception as e:
            print(f"❌ Ошибка скачивания с lmusic.kz: {e}")
            import traceback
            traceback.print_exc()
            return None

