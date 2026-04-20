# 🎵 Music Bot

Telegram бот для поиска и скачивания музыки из разных источников.

## 🎯 Возможности

- 🔍 Поиск музыки в 3 источниках:
  - 🔵 **Deezer** - международная музыка
  - 🟡 **Яндекс.Музыка** - русская музыка
  - 🎵 **Music Original** - оригиналы без цензуры (lmusic.kz)
  
- 💾 Скачивание треков в MP3
- ❤️ Избранное
- 🎧 Топ-20 чарта Яндекс.Музыки
- 📊 Статистика для админов
- 🗄️ База данных пользователей и истории

## 🚀 Быстрый старт

### Локальный запуск

1. Установи зависимости:
```bash
pip install -r requirements.txt
```

2. Создай файл `.env`:
```env
BOT_TOKEN=твой_токен_бота
PROXY_URL=http://127.0.0.1:12334
```

3. Запусти бота:
```bash
python bot/main.py
```

### Деплой на Render

Смотри инструкцию в [DEPLOY_RENDER.md](DEPLOY_RENDER.md)

## 📁 Структура проекта

```
Music_bot/
├── api/                    # API для источников музыки
│   ├── deezer_api.py      # Deezer API
│   ├── yandex_api.py      # Яндекс.Музыка API
│   ├── mp3party_parser.py # Парсер lmusic.kz
│   ├── downloader.py      # Скачивание через yt-dlp
│   └── music_search.py    # Общий поиск
├── bot/                    # Telegram бот
│   ├── main.py            # Точка входа
│   ├── handlers.py        # Обработчики команд
│   └── keyboards.py       # Клавиатуры
├── config/                 # Настройки
│   └── settings.py        # Конфигурация
├── database/               # База данных
│   ├── db.py              # Подключение к БД
│   └── models.py          # Модели SQLAlchemy
└── requirements.txt        # Зависимости
```

## 🛠️ Технологии

- **aiogram 3.x** - Telegram Bot API
- **yt-dlp** - Скачивание с YouTube
- **SQLAlchemy** - ORM для базы данных
- **aiohttp** - Асинхронные HTTP запросы
- **BeautifulSoup4** - Парсинг HTML
- **yandex-music** - API Яндекс.Музыки

## 📊 Админ-панель

Для доступа к статистике добавь свой Telegram ID в `config/settings.py`:

```python
ADMIN_IDS = [
    твой_telegram_id,
]
```

Админам доступна кнопка "📊 Статистика" с информацией:
- Количество пользователей
- Количество скачиваний
- Популярные источники

## 📝 Лицензия

MIT License

## 👨‍💻 Автор

@Music_good_bot
