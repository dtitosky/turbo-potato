import os
import psycopg2
from psycopg2.extras import DictCursor
from config import DATABASE_URL

def get_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL не установлен в переменных окружения")
    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
        print("Успешное подключение к базе данных")
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        raise

def create_tables():
    """
    Создаёт таблицы, если их нет. Выполнять при старте приложения.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Ваш SQL код для создания таблиц
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username TEXT
                )
            """)
            conn.commit()
    finally:
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