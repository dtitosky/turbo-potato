import os
from dotenv import load_dotenv

# Загружаем переменные из .env (если они присутствуют) – на Railway переменные задаются через интерфейс
load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN не установлен в переменных окружения")

# Подключение к PostgreSQL через переменные окружения
# Обычно Railway передаёт URL в переменную DATABASE_URL
# Например: postgres://user:password@host:port/dbname
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не установлен в переменных окружения")

# Можно добавить другие настройки, например, ключи для OCR, REST API, и т.д. 

# Для отладки можно вывести доступные переменные (не рекомендуется в продакшене)
#print("DEBUG ENV:", os.environ) 