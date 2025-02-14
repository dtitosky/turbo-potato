API_TOKEN = "ВАШ_TELEGRAM_BOT_TOKEN"

# Подключение к PostgreSQL через переменные окружения
# Обычно Railway передаёт URL в переменную DATABASE_URL
# Например: postgres://user:password@host:port/dbname
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgres://user:pass@localhost:5432/dbname")

# Можно добавить другие настройки, например, ключи для OCR, REST API, и т.д. 