import sqlite3

from config.config import Config
from data.code_sample import CodeSample
from data.code_smell import CodeSmell
from services.openai_client import OpenAIClient

SMELL_AMOUNTS = {
    'blob': {'none': 30, 'minor': 5, 'major': 3, 'critical': 2},
    'data class': {'none': 29, 'minor': 5, 'major': 4, 'critical': 2},
    'long method': {'none': 30, 'minor': 5, 'major': 3, 'critical': 2},
    'feature envy': {'none': 34, 'minor': 3, 'major': 2, 'critical': 1}
}


class Analyzer:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_PATH)
        self.openai_client = OpenAIClient(Config.ASSISTANT_ID)
        self.results = {}

    def run(self, ids=None):
        ids = self.get_ids() if ids is None else [ids]

        # Get distinct code sample ids
        code_sample_ids = CodeSmell.get_code_sample_ids(self.conn, ids)
        for code_sample_id in code_sample_ids:
            # Get all related smells to the code sample
            smells = CodeSample.get_related_smells(self.conn, code_sample_id)
            sample = CodeSample.get_by_id(self.conn, code_sample_id)
            response = self.openai_client.get_response(sample.code_segment)

            for smell in smells:
                if smell.smell not in self.results:
                    self.initialize_results(smell.smell)

                # Check if the smell is present in the response
                smell_is_present = any(
                    smell.get_name() == given_smell['name'] and
                    self.results[smell.smell][smell.severity].update(
                        # Update the count of the severity
                        {given_smell['severity']: self.results[smell.smell][smell.severity].get(given_smell['severity'],
                                                                                                0) + 1}
                    )
                    for given_smell in response['smells']
                )

                # If the smell is not present, update the count of none
                if not smell_is_present:
                    self.results[smell.smell][smell.severity]['none'] += 1

    def initialize_results(self, smell_name):
        self.results[smell_name] = {'none': {'none': 0, 'minor': 0, 'major': 0, 'critical': 0},
                                    'minor': {'none': 0, 'minor': 0, 'major': 0, 'critical': 0},
                                    'major': {'none': 0, 'minor': 0, 'major': 0, 'critical': 0},
                                    'critical': {'none': 0, 'minor': 0, 'major': 0, 'critical': 0}}

    def get_ids(self):
        ids = []
        for smell, severity_amounts in SMELL_AMOUNTS.items():
            for severity, amount in severity_amounts.items():
                ids.extend(CodeSmell.get_ids(self.conn, smell, severity, amount))
        return ids

