import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='database.db'):
        self.db_name = db_name
        self._init_db()
    
    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_id TEXT NOT NULL,
                    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT DEFAULT ''
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anon (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    message_id INTEGER,
                    message TEXT''
                )
            ''')
            conn.commit()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def save_menu(self, file_ids: list[str], description: str = ''):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute('DELETE FROM menu')

            for file_id in file_ids:
                cursor.execute(
                    'INSERT INTO menu (file_id, description) VALUES (?, ?)',
                    (file_id, description)
                )
            conn.commit()
    
    def get_all_menu_photos(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT file_id, description, date_added 
                FROM menu 
                ORDER BY date_added
            ''')
            return cursor.fetchall()
    
    def get_latest_menu(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT file_id, description, date_added 
                FROM menu 
                ORDER BY date_added DESC 
                LIMIT 1
            ''')
            return cursor.fetchone()
    
    def get_menu_history(self, limit: int = 5):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT file_id, description, date_added 
                FROM menu 
                ORDER BY date_added DESC 
                LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
        
    def save_anonym_message(self, user_id: int, message_id: int, message: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO anon (user_id, message_id, message) VALUES (?, ?, ?)",
                    (user_id, message_id, message))
            conn.commit()

    def get_user_for_answer(self, message_id:int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, message
                FROM anon 
                WHERE message_id = ?
            ''', (message_id,))
            return cursor.fetchall()

db = Database()