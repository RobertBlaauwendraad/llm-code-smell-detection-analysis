import csv

from config.config import Config
from data import initialize_database
from data.code_sample import CodeSample
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
        for entry in dataset:
            # Skip if id is not in the range
            if id_range and int(entry['id']) not in id_range:
                continue

            code_segment = self.gh_repository.get_extended_segment(entry['repository'], entry['commit_hash'],
                                                                   entry['path'],
                                                                   int(entry['start_line']))
            # Skip if code_segment is empty
            if not code_segment:
                continue

            # Save the CodeSample if it doesn't exist
            cursor.execute(
                '''SELECT id FROM CodeSample WHERE repository = ? AND commit_hash = ? AND path = ? AND code_segment = ?''',
                (entry['repository'], entry['commit_hash'], entry['path'], code_segment))
            sample_id = cursor.fetchone()
            if not sample_id:
                sample_id = CodeSample(entry['sample_id'], entry['repository'], entry['commit_hash'], entry['path'],
                                       code_segment).save(self.conn)
            else:
                sample_id = sample_id[0]

            # Save the CodeScope if it doesn't exist
            if not cursor.execute('''SELECT 1 FROM CodeSmell WHERE id = ?''', (entry['id'],)).fetchone():
                CodeSmell(entry['id'], sample_id, entry['smell'], entry['severity'], entry['code_name'],
                          entry['start_line'], entry['end_line'], entry['link']).save(self.conn)


if __name__ == '__main__':
    initializer = Initializer()
    initializer.populate_database()
