import psycopg2
from psycopg2.extras import DictCursor
from config import DATABASE_URL

def get_connection():
    """
    Создаёт подключение к БД и возвращает его.
    """
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    return conn

def create_tables():
    """
    Создаёт таблицы, если их нет. Выполнять при старте приложения.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blood_tests (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            test_text TEXT,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_blood_test(user_id: int, test_text: str):
    """
    Сохраняет распознанный текст анализа крови в БД.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO blood_tests (user_id, test_text)
        VALUES (%s, %s)
    """, (user_id, test_text))
    conn.commit()
    cur.close()
    conn.close()

def get_user_tests(user_id: int):
    """
    Возвращает все анализы пользователя.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM blood_tests
        WHERE user_id = %s
        ORDER BY timestamp DESC
    """, (user_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows 