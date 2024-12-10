import csv

from github3.exceptions import ForbiddenError

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
        try:
            cursor = self.conn.cursor()
            dataset = get_dataset()
            for entry in dataset:
                # Skip if id is not in the range
                if id_range and int(entry['id']) not in id_range:
                    continue

                # Check if the CodeSample exists using repository, commit_hash, and path
                cursor.execute(
                    '''SELECT id, code_segment FROM CodeSample WHERE repository = ? AND commit_hash = ? AND path = ?''',
                    (entry['repository'], entry['commit_hash'], entry['path']))
                sample = cursor.fetchone()

                if not sample:
                    print(f'Fetching code segment for {entry["repository"]} {entry["commit_hash"]} {entry["path"]}')

                    # Get the code segment since it doesn't exist
                    if entry['type'] == 'class':
                        code_segment = self.gh_repository.get_segment(entry['repository'], entry['commit_hash'],
                                                                      entry['path'], int(entry['start_line']),
                                                                      int(entry['end_line']))
                    else:
                        code_segment = self.gh_repository.get_extended_segment(entry['repository'],
                                                                               entry['commit_hash'],
                                                                               entry['path'],
                                                                               int(entry['start_line']))

                    # Save the new CodeSample
                    sample_id = CodeSample(entry['sample_id'], entry['repository'], entry['commit_hash'], entry['path'],
                                           code_segment).save(self.conn)
                    print(f'Saving CodeSample {sample_id}')
                else:
                    sample_id = sample[0]
                    code_segment = sample[1]
                    print(f'CodeSample already exists for {entry["repository"]} {entry["commit_hash"]} {entry["path"]}')

                # Save the CodeScope if it doesn't exist and sample_id is not None
                if not cursor.execute('''SELECT 1 FROM CodeSmell WHERE id = ?''',
                                      (entry['id'],)).fetchone() and sample_id:
                    if code_segment is None:
                        print(f'Code segment is None for {entry["id"]}')
                        CodeSmell(entry['id'], sample_id, None, None, None, None, None, None, None).save(self.conn)
                    else:
                        print(f'Saving CodeSmell {entry["id"]}')
                        CodeSmell(entry['id'], sample_id, entry['smell'], entry['severity'], entry['type'],
                                  entry['code_name'],
                                  entry['start_line'], entry['end_line'], entry['link']).save(self.conn)

        except ForbiddenError as e:
            print(f'ForbiddenError: {e}')

    def show_rate_limit(self):
        print(self.gh_repository.get_rate_limit()['resources']['core'])


if __name__ == '__main__':
    initializer = Initializer()
    initializer.populate_database()
    initializer.show_rate_limit()
