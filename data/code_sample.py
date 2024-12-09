class CodeSample:
    def __init__(self, sample_id, repository, commit_hash, path, code_segment):
        self.id = sample_id
        self.repository = repository
        self.commit_hash = commit_hash
        self.path = path
        self.code_segment = code_segment

    def save(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO CodeSample(repository, commit_hash, path, code_segment)
            VALUES (?, ?, ?, ?)
        ''', (self.repository, self.commit_hash, self.path, self.code_segment))
        conn.commit()
        return cursor.lastrowid

    @staticmethod
    def get_by_id(conn, sample_id):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM CodeSample WHERE id = ?
        ''', (sample_id,))
        result = cursor.fetchone()
        if result:
            return CodeSample(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
        return None

    def __str__(self):
        return f'{self.repository} {self.commit_hash} {self.path} {self.start_line} {self.end_line}'
