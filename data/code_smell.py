class CodeSmell:
    def __init__(self, smell_id, code_sample_id, smell_type, severity, reviewer_id, review_timestamp):
        self.id = smell_id
        self.code_sample_id = code_sample_id
        self.smell_type = smell_type
        self.severity = severity
        self.reviewer_id = reviewer_id
        self.review_timestamp = review_timestamp

    def save(self, conn):
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO CodeSmell(id, code_sample_id, smell_type, severity, reviewer_id, review_timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.id, self.code_sample_id, self.smell_type, self.severity, self.reviewer_id, self.review_timestamp))
        conn.commit()

    @staticmethod
    def get_smells_by_ids(conn, ids):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM CodeSmell WHERE id IN ({})
        '''.format(','.join('?' * len(ids))), ids)
        rows = cursor.fetchall()
        smells = []
        for row in rows:
            smells.append(CodeSmell(row[0], row[1], row[2], row[3], row[4], row[5]))
        return smells

    @staticmethod
    def get_smells_by_range(conn, start, end):
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM CodeSmell WHERE id BETWEEN ? AND ?
        ''', (start, end))
        rows = cursor.fetchall()
        smells = []
        for row in rows:
            smells.append(CodeSmell(row[0], row[1], row[2], row[3], row[4], row[5]))
        return smells

    @staticmethod
    def get_development_ids(conn, smell_type, severity, scope, limit=None):
        cursor = conn.cursor()

        query = '''
            SELECT cs.id FROM CodeSmell cs
            JOIN CodeScope sc ON cs.code_sample_id = sc.sample_id AND sc.scope_type = ?
            WHERE cs.smell_type = ? AND cs.severity = ? AND sc.code_segment IS NOT NULL AND cs.code_sample_id IN (
                SELECT code_sample_id FROM CodeSmell WHERE smell_type != ? AND severity = 'none'
            )
        '''
        params = [scope, smell_type, severity, smell_type]
        if limit:
            query += ' LIMIT ?'
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def __str__(self):
        return f'{self.code_sample_id} {self.smell_type} {self.severity}'
