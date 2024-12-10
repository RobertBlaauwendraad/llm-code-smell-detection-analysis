import sqlite3

from config.config import Config


def initialize_database():
    conn = sqlite3.connect(Config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CodeSample(
            id INTEGER PRIMARY KEY,
            repository TEXT,
            commit_hash TEXT,
            path TEXT,
            code_segment TEXT,
            UNIQUE(repository, commit_hash, path)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CodeSmell (
            id INTEGER PRIMARY KEY,
            code_sample_id INTEGER,
            smell TEXT,
            severity TEXT,
            scope TEXT,
            code_name TEXT,
            start_line INTEGER,
            end_line INTEGER,
            link TEXT,
            FOREIGN KEY (code_sample_id) REFERENCES CodeSample(id)
        )
    ''')
    conn.commit()
    return conn
