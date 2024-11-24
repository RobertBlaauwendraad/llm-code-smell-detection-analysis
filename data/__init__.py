import sqlite3


def initialize_database():
    conn = sqlite3.connect('data/code_smell_analysis.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CodeSample(
            id INTEGER PRIMARY KEY,
            repository TEXT,
            commit_hash TEXT,
            path TEXT,
            start_line INTEGER,
            end_line INTEGER,
            link TEXT,
            UNIQUE(repository, commit_hash, path, start_line, end_line)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CodeScope (
            id INTEGER PRIMARY KEY,
            sample_id INTEGER,
            scope_type TEXT,
            code_segment TEXT,
            FOREIGN KEY (sample_id) REFERENCES CodeSample(id),
            UNIQUE(sample_id, scope_type)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS CodeSmell (
            id INTEGER PRIMARY KEY,
            code_sample_id INTEGER,
            smell_type TEXT,
            severity TEXT,
            reviewer_id INTEGER,
            review_timestamp TEXT,
            FOREIGN KEY (code_sample_id) REFERENCES CodeSample(id)
        )
    ''')
    conn.commit()
    return conn
