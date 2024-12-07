import csv

from config.config import Config
from data import initialize_database
from data.code_sample import CodeSample
from data.code_scope import CodeScope
from data.code_smell import CodeSmell
from repository.repository import Repository

def get_dataset():
    with open(Config.DATASET_PATH, 'r') as csvfile:
        return list(csv.DictReader(csvfile, delimiter=';'))


class Initializer:
    def __init__(self):
        self.gh_repository = Repository()
        self.conn = initialize_database()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def populate_database(self, id_range=None):
        cursor = self.conn.cursor()
        dataset = get_dataset()
        for data in dataset:
            # Skip if id is not in the range
            if id_range and int(data['id']) not in id_range:
                continue

            # Skip if the CodeSample already exists
            if not cursor.execute(
                    '''SELECT * FROM CodeSample WHERE repository = ? AND commit_hash = ? AND path = ? AND start_line = ? AND end_line = ?''',
                    (data['repository'], data['commit_hash'], data['path'], data['start_line'],
                     data['end_line'])).fetchone():
                CodeSample(data['sample_id'], data['repository'], data['commit_hash'], data['path'], data['start_line'],
                           data['end_line'], data['link']).save(self.conn)

            # Skip if the CodeScope already exists
            if not cursor.execute('''SELECT * FROM CodeScope WHERE sample_id = ? AND scope_type = ?''',
                                  (data['sample_id'], data['type'])).fetchone():
                code_segment = self.gh_repository.get_segment(data['repository'], data['commit_hash'], data['path'],
                                                              int(data['start_line']), int(data['end_line']))
                CodeScope(data['sample_id'], data['type'], code_segment).save(self.conn)

            # Skip if the CodeSmell already exists
            if not cursor.execute('''SELECT * FROM CodeSmell WHERE id = ?''',
                                  (data['id'],)).fetchone():
                CodeSmell(data['id'], data['sample_id'], data['smell'], data['severity'], data['reviewer_id'],
                          data['review_timestamp']).save(self.conn)

            # Extend function scope to class scope
            if data['type'] == 'function':
                if not cursor.execute('''SELECT * FROM CodeScope WHERE sample_id = ? AND scope_type = ?''',
                                      (data['sample_id'], 'class')).fetchone():
                    extended_code_segment = self.gh_repository.get_extended_segment(data['repository'], data['commit_hash'], data['path'],
                                                              int(data['start_line']), int(data['end_line']))
                    CodeScope(data['sample_id'], 'extended_function', extended_code_segment).save(self.conn)


if __name__ == '__main__':
    initializer = Initializer()
    initializer.populate_database()
