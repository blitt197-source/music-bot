# 🎵 Как получить Spotify API ключи

## Шаг 1: Регистрация в Spotify for Developers

1. Открой: https://developer.spotify.com/dashboard
2. Нажми **"Log in"** (войди через свой Spotify аккаунт)
3. Если нет аккаунта - создай бесплатный на https://spotify.com

## Шаг 2: Создание приложения

1. На странице Dashboard нажми **"Create app"**
2. Заполни форму:
   - **App name**: `Music Bot` (или любое название)
   - **App description**: `Telegram bot for music search`
   - **Redirect URI**: `http://localhost:8888/callback` (можно любой)
   - **Which API/SDKs are you planning to use?**: выбери **Web API**
3. Согласись с условиями
4. Нажми **"Save"**

## Шаг 3: Получение ключей

1. Открой созданное приложение
2. Нажми **"Settings"** (справа вверху)
3. Найди:
   - **Client ID** - скопируй
   - **Client Secret** - нажми "View client secret" и скопируй

## Шаг 4: Добавление в проект

1. Открой файл `.env` в проекте
2. Вставь свои ключи:
   ```
   SPOTIFY_CLIENT_ID=твой_client_id
   SPOTIFY_CLIENT_SECRET=твой_client_secret
   ```

## Шаг 5: Перезапуск бота

1. Останови бота (Ctrl+C)
2. Установи новые библиотеки: `pip install -r requirements.txt`
3. Запусти снова: `python bot/main.py`

## ✅ Проверка

В логах должно появиться:
```
✅ Spotify API подключен
✅ Яндекс.Музыка подключена
```

Теперь при поиске будут реальные треки из Spotify и Яндекс.Музыки!

## 🟢 Обозначения в боте:

- 🟢 - трек из Spotify
- 🟡 - трек из Яндекс.Музыки
- ⚪ - тестовые данные (если API не работают)

---

**Важно:** Spotify API бесплатный, но есть лимиты (обычно достаточно для личного использования).
