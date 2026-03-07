import sqlite3
import json
from datetime import datetime


DEFAULT_SCHEDULE = {
    "Пн": ["Подтягивания", "Пресс + скручивания"],
    "Вт": ["Приседания", "Выпады"],
    "Ср": ["Отдых"],
    "Чт": ["Подтягивания", "Пресс + скручивания"],
    "Пт": ["Приседания", "Выпады"],
    "Сб": ["Отдых"],
    "Вс": ["Подтягивания", "Пресс + скручивания"]
}


class Database:
    def __init__(self, db_path="workout_profiles.db"):
        self.db_path = db_path
        self.init_database()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def init_database(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                name TEXT PRIMARY KEY,
                full_name TEXT,
                gender TEXT,
                height TEXT,
                weight REAL,
                last_used TEXT,
                workouts TEXT,
                schedule TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def load_profiles_list(self):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM profiles")
        profiles = [row[0] for row in cursor.fetchall()]
        conn.close()
        return profiles

    def load_profile(self, name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT full_name, gender, height, weight, workouts, schedule
            FROM profiles WHERE name = ?
        ''', (name,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return None

        workouts = json.loads(result[4]) if result[4] else []
        schedule = json.loads(result[5]) if result[5] else DEFAULT_SCHEDULE

        for w in workouts:
            if "time" not in w:
                w["time"] = "--:--"

        return {
            "profile": {
                "full_name": result[0] or "",
                "gender":    result[1] or "",
                "height":    result[2] or "",
                "weight":    result[3] or ""
            },
            "workouts": workouts,
            "schedule": schedule
        }

    def save_profile(self, name, profile, workouts, schedule):
        conn = self.connect()
        cursor = conn.cursor()

        weight_val = profile.get("weight", "")
        if isinstance(weight_val, str) and weight_val.replace('.', '', 1).isdigit():
            weight_val = float(weight_val)
        elif isinstance(weight_val, (int, float)):
            weight_val = float(weight_val)
        else:
            weight_val = 0.0

        cursor.execute('''
            INSERT OR REPLACE INTO profiles
            (name, full_name, gender, height, weight, workouts, schedule, last_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            profile.get("full_name", ""),
            profile.get("gender", ""),
            profile.get("height", ""),
            weight_val,
            json.dumps(workouts, ensure_ascii=False),
            json.dumps(schedule, ensure_ascii=False),
            datetime.now().strftime("%d.%m.%Y %H:%M")
        ))
        conn.commit()
        conn.close()

    def create_profile(self, name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO profiles (name, last_used)
            VALUES (?, ?)
        ''', (name, datetime.now().strftime("%d.%m.%Y %H:%M")))
        conn.commit()
        conn.close()

    def delete_profile(self, name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM profiles WHERE name = ?", (name,))
        conn.commit()
        conn.close()

    def update_last_used(self, name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE profiles SET last_used = ? WHERE name = ?",
            (datetime.now().strftime("%d.%m.%Y %H:%M"), name)
        )
        conn.commit()
        conn.close()

    def get_last_used(self, name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT last_used FROM profiles WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result and result[0] else "Неизвестно"

    def profile_exists(self, name):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM profiles WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        return result is not None