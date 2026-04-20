# Деплой бота на Render.com

## Шаг 1: Подготовка репозитория

1. Создай репозиторий на GitHub
2. Загрузи все файлы проекта:
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/music-bot.git
git push -u origin main
```

## Шаг 2: Создание сервиса на Render

1. Зайди на [render.com](https://render.com)
2. Нажми "New +" → "Web Service"
3. Подключи свой GitHub репозиторий
4. Выбери репозиторий `music-bot`

## Шаг 3: Настройка сервиса

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
python bot/main.py
```

**Environment:**
- Python 3

**Plan:**
- Free (или Starter если нужна стабильность)

## Шаг 4: Переменные окружения

Добавь следующие переменные в разделе "Environment":

```
BOT_TOKEN=8708352687:AAGzhUrPCc-BD0p-OZns_MB8EthnGHQ2WEg
PROXY_URL=http://127.0.0.1:12334
DATABASE_URL=sqlite+aiosqlite:///./music_bot.db
```

⚠️ **ВАЖНО:** На Render прокси `http://127.0.0.1:12334` работать не будет!
Нужно либо:
- Убрать прокси (если Render не блокирует Telegram)
- Использовать внешний прокси сервис

## Шаг 5: Деплой

1. Нажми "Create Web Service"
2. Render автоматически:
   - Склонирует репозиторий
   - Установит зависимости
   - Запустит бота

## Шаг 6: Проверка

1. Открой логи в Render Dashboard
2. Должно появиться:
```
✅ Deezer API подключен (бесплатный)
✅ LMusic.kz парсер подключен (Music Original)
✅ Яндекс.Музыка подключена
🔒 Используется прокси: http://127.0.0.1:12334
🚀 Бот запущен!
```

3. Напиши боту в Telegram - он должен ответить

## Проблемы и решения

### Бот не отвечает
- Проверь что BOT_TOKEN правильный
- Проверь логи на наличие ошибок
- Убедись что прокси работает (или отключи его)

### База данных не работает
- Render Free план использует эфемерное хранилище
- База будет сбрасываться при каждом деплое
- Для постоянной БД используй PostgreSQL (платно)

### FFmpeg не найден
- На Render FFmpeg нужно установить отдельно
- Добавь в `render.yaml`:
```yaml
buildCommand: |
  apt-get update
  apt-get install -y ffmpeg
  pip install -r requirements.txt
```

## Альтернатива: Запуск локально 24/7

Если Render не подходит, можешь запустить бота на своём компьютере:

```bash
python bot/main.py
```

Компьютер должен быть включен постоянно.

## Мониторинг

- Логи: Render Dashboard → Logs
- Статус: Render Dashboard → Events
- Рестарт: Render Dashboard → Manual Deploy → "Clear build cache & deploy"

---

Готово! Бот будет работать 24/7 на Render.
