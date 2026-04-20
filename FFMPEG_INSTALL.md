# 🎵 Установка FFmpeg для скачивания музыки

FFmpeg нужен для конвертации аудио в MP3 формат.

## Windows (твоя система):

### Способ 1: Через Chocolatey (рекомендую)

1. Открой PowerShell **от имени администратора**
2. Установи Chocolatey (если нет):
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```
3. Установи FFmpeg:
   ```powershell
   choco install ffmpeg
   ```

### Способ 2: Вручную

1. Скачай FFmpeg: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. Распакуй архив (например в `C:\ffmpeg`)
3. Добавь в PATH:
   - Открой "Система" → "Дополнительные параметры системы"
   - "Переменные среды"
   - В "Системные переменные" найди `Path`
   - Добавь путь к папке `bin` (например: `C:\ffmpeg\bin`)
4. Перезапусти командную строку

### Проверка установки:

Открой командную строку и выполни:
```bash
ffmpeg -version
```

Должна показаться версия FFmpeg.

---

## После установки FFmpeg:

1. Перезапусти командную строку
2. Установи обновлённые зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Запусти бота:
   ```bash
   python bot/main.py
   ```

Теперь скачивание должно работать! 🚀
