class CodeScope:
    def __init__(self, sample_id, scope_type, code_segment=None):
        self.id = None
        self.sample_id = sample_id
        self.scope_type = scope_type
        self.code_segment = code_segment

    def save(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO CodeScope(sample_id, scope_type, code_segment)
            VALUES (?, ?, ?)
        ''', (self.sample_id, self.scope_type, self.code_segment))
        conn.commit()
        cursor.execute('''
            SELECT id FROM CodeScope WHERE sample_id = ? AND scope_type = ? 
        ''', (self.sample_id, self.scope_type))
        result = cursor.fetchone()
        if result:
            self.id = result[0]
            return True
        return False

    @staticmethod
    def get_by_id_and_type(conn, sample_id, scope_type):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM CodeScope WHERE sample_id = ? AND scope_type = ?
        ''', (sample_id, scope_type))
        result = cursor.fetchone()
        if result:
            code_scope = CodeScope(result[1], result[2], result[3])
            code_scope.id = result[0]
            return code_scope
        return None

    def __str__(self):
        return f'{self.sample_id} {self.scope_type}'
