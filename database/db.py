"""
Работа с базой данных
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from database.models import Base, User, Favorite, DownloadHistory
from datetime import datetime
from typing import List, Optional


class Database:
    """Класс для работы с БД"""
    
    def __init__(self, db_url: str):
        """
        Инициализация БД
        
        Args:
            db_url: URL подключения к БД
        """
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def init_db(self):
        """Создать таблицы"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ База данных инициализирована")
    
    async def add_user(self, telegram_id: int, username: str = None, first_name: str = None):
        """Добавить пользователя"""
        async with self.async_session() as session:
            # Проверяем есть ли уже
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name
                )
                session.add(user)
                await session.commit()
            else:
                # Обновляем last_active
                user.last_active = datetime.utcnow()
                await session.commit()
    
    async def add_to_favorites(self, user_id: int, track_title: str, track_artist: str, 
                               track_album: str = None, source: str = None):
        """Добавить в избранное"""
        async with self.async_session() as session:
            # Проверяем нет ли уже
            result = await session.execute(
                select(Favorite).where(
                    Favorite.user_id == user_id,
                    Favorite.track_title == track_title,
                    Favorite.track_artist == track_artist
                )
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                favorite = Favorite(
                    user_id=user_id,
                    track_title=track_title,
                    track_artist=track_artist,
                    track_album=track_album,
                    source=source
                )
                session.add(favorite)
                await session.commit()
                return True
            return False
    
    async def remove_from_favorites(self, user_id: int, favorite_id: int):
        """Удалить из избранного"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Favorite).where(
                    Favorite.id == favorite_id,
                    Favorite.user_id == user_id
                )
            )
            favorite = result.scalar_one_or_none()
            
            if favorite:
                await session.delete(favorite)
                await session.commit()
                return True
            return False
    
    async def get_favorites(self, user_id: int, limit: int = 50) -> List[Favorite]:
        """Получить избранное пользователя"""
        async with self.async_session() as session:
            result = await session.execute(
                select(Favorite)
                .where(Favorite.user_id == user_id)
                .order_by(Favorite.added_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def add_download_history(self, user_id: int, track_title: str, 
                                   track_artist: str, source: str = None):
        """Добавить в историю скачиваний"""
        async with self.async_session() as session:
            history = DownloadHistory(
                user_id=user_id,
                track_title=track_title,
                track_artist=track_artist,
                source=source
            )
            session.add(history)
            await session.commit()
    
    async def get_download_history(self, user_id: int, limit: int = 20) -> List[DownloadHistory]:
        """Получить историю скачиваний"""
        async with self.async_session() as session:
            result = await session.execute(
                select(DownloadHistory)
                .where(DownloadHistory.user_id == user_id)
                .order_by(DownloadHistory.downloaded_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def get_user_stats(self, user_id: int) -> dict:
        """Получить статистику пользователя"""
        async with self.async_session() as session:
            # Количество скачиваний
            downloads_result = await session.execute(
                select(DownloadHistory).where(DownloadHistory.user_id == user_id)
            )
            downloads_count = len(downloads_result.scalars().all())
            
            # Количество избранного
            favorites_result = await session.execute(
                select(Favorite).where(Favorite.user_id == user_id)
            )
            favorites_count = len(favorites_result.scalars().all())
            
            return {
                'downloads': downloads_count,
                'favorites': favorites_count
            }
