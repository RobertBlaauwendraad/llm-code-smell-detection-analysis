import sqlite3

import pandas as pd

from services.openai_client import OpenAIClient
from config.config import Config

class BaseSmellAnalyzer:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_PATH)
        self.client = OpenAIClient()
        self.results = {'correct': {}, 'incorrect': {}}

    @staticmethod
    def compare_results(code_smell, openai_response):
        for smell in openai_response['smells']:
            if code_smell.smell_type == smell['name']:
                if code_smell.severity == smell['severity']:
                    return True
                else:
                    return False

    def count_results(self, openai_response, scope, smells):
        for smell in smells:
            if smell.code_sample_id == scope.sample_id:
                if self.compare_results(smell, openai_response):
                    if smell.smell_type not in self.results['correct']:
                        self.results['correct'][smell.smell_type] = {}
                    if smell.severity not in self.results['correct'][smell.smell_type]:
                        self.results['correct'][smell.smell_type][smell.severity] = 0
                    self.results['correct'][smell.smell_type][smell.severity] += 1
                else:
                    if smell.smell_type not in self.results['incorrect']:
                        self.results['incorrect'][smell.smell_type] = {}
                    if smell.severity not in self.results['incorrect'][smell.smell_type]:
                        self.results['incorrect'][smell.smell_type][smell.severity] = 0
                    self.results['incorrect'][smell.smell_type][smell.severity] += 1

    def view_results(self):
        correct_df = pd.DataFrame(self.results['correct']).fillna(0).astype(int)
        incorrect_df = pd.DataFrame(self.results['incorrect']).fillna(0).astype(int)
        print('Correct')
        print(correct_df)
        print('Incorrect')
        print(incorrect_df)