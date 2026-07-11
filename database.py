import sqlite3
import os

DB_FILE = "pet_health.db"


class DatabaseManager:
    def __init__(self):
        self.conn = None

    #создание таблицы при первом запуске
    def init_db(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                species TEXT,
                vaccine TEXT,
                date TEXT,
                vet TEXT,
                image_path TEXT)""")
        self.conn.commit()

    #получение всех записей
    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM pets ORDER BY name")
        return cursor.fetchall()

    #добавление записи
    def insert_record(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO pets (name, species, vaccine, date, vet, image_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (data["name"], data["species"], data["vaccine"],
              data["date"], data["vet"], data.get("image_path", "")))
        self.conn.commit()

    #обновление записи
    def update_record(self, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE pets 
            SET name=?, species=?, vaccine=?, date=?, vet=?, image_path=?
            WHERE id=?
        """, (data["name"], data["species"], data["vaccine"],
              data["date"], data["vet"],  data.get("image_path", ""), data["id"]))
        self.conn.commit()

    #удаление записи
    def delete_record(self, item_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM pets WHERE id=?", (item_id,))
        self.conn.commit()

    #закрытие соединения с бд
    def close(self):
        if self.conn:
            self.conn.close()