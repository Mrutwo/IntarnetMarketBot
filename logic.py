import sqlite3

DB_NAME = 'support_bot.db'

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            question TEXT,
            status TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER,
            response TEXT,
            FOREIGN KEY(question_id) REFERENCES questions(id)
        )
    ''')

    conn.commit()
    conn.close()

def save_custom_question(user_id, username, question):
    """Сохранение пользовательского вопроса в базу данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO questions (user_id, username, question, status)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, question, 'pending'))

    conn.commit()
    question_id = cursor.lastrowid
    conn.close()

    return question_id

def find_similar_question(user_question):
    """Поиск похожих вопросов в базе данных и возвращение ответа"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    conn.close()
    return None

def save_response(request_id, response):
    """Сохранение ответа на вопрос в базе данных"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE questions
        SET status = ?
        WHERE id = ?
    ''', ('answered', request_id))

    cursor.execute('''
        INSERT INTO responses (question_id, response)
        VALUES (?, ?)
    ''', (request_id, response))

    conn.commit()
    conn.close()

def get_pending_requests():
    """Возвращает список запросов, ожидающих ответа"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, question
        FROM questions
        WHERE status = 'pending'
    ''')

    requests = cursor.fetchall()
    conn.close()
    return requests

def get_request_details(request_id):
    """Возвращает детали запроса по request_id"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT user_id, question
        FROM questions
        WHERE id = ?
    ''', (request_id,))

    details = cursor.fetchone()
    conn.close()
    return details
