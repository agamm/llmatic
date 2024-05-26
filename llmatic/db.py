import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".llmatic" / "llmatic.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trackings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT,
            tracking_id TEXT,
            execution_time_ms INTEGER,
            input TEXT,
            output TEXT,
            eval_results TEXT,
            created_at TEXT,
            model TEXT,
            prompt_cost REAL,
            completion_cost REAL,
            total_cost REAL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            total_tokens INTEGER
        )
    ''')
    conn.commit()
    conn.close()
