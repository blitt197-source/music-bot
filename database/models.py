"""
Модели базы данных
"""
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)


class Favorite(Base):
    """Модель избранного"""
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    track_title = Column(String(500), nullable=False)
    track_artist = Column(String(500), nullable=False)
    track_album = Column(String(500))
    source = Column(String(50))  # deezer, yandex, soundcloud
    added_at = Column(DateTime, default=datetime.utcnow)


class DownloadHistory(Base):
    """История скачиваний"""
    __tablename__ = 'download_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    track_title = Column(String(500), nullable=False)
    track_artist = Column(String(500), nullable=False)
    source = Column(String(50))
    downloaded_at = Column(DateTime, default=datetime.utcnow)
