import sqlite3

import pandas as pd

from config.config import Config
from data.code_sample import CodeSample
from data.code_scope import CodeScope
from data.code_smell import CodeSmell
from repository import Repository
from services.openai_client import OpenAIClient


class Main:
    def __init__(self):
        self.repository = Repository()
        self.conn = sqlite3.connect('../data/code_smell_analysis.db')
        self.client = OpenAIClient()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def analyze_function_smells(self, start_id, end_id):
        smells = CodeSmell.get_smells_by_range(self.conn, start_id, end_id)
        scopes = {}
        results = {'correct': {}, 'incorrect': {}}

        for smell in smells:
            code_sample = CodeSample.get_by_id(self.conn, smell.code_sample_id)
            code_scope = CodeScope.get_by_id_and_type(self.conn, code_sample.id, 'function')
            if code_scope and code_scope.id not in scopes:
                scopes[code_scope.id] = code_scope

        for scope_id, scope in scopes.items():
            openai_response = self.client.get_response(Config.FUNCTION_SMELL_ASSISTANT_ID, scope.code_segment)
            for smell in smells:
                if smell.code_sample_id == scope.sample_id:
                    if self.compare_results(smell, openai_response):
                        if smell.smell_type not in results['correct']:
                            results['correct'][smell.smell_type] = {}
                        if smell.severity not in results['correct'][smell.smell_type]:
                            results['correct'][smell.smell_type][smell.severity] = 0
                        results['correct'][smell.smell_type][smell.severity] += 1
                    else:
                        if smell.smell_type not in results['incorrect']:
                            results['incorrect'][smell.smell_type] = {}
                        if smell.severity not in results['incorrect'][smell.smell_type]:
                            results['incorrect'][smell.smell_type][smell.severity] = 0
                        results['incorrect'][smell.smell_type][smell.severity] += 1
        return results

    @staticmethod
    def compare_results(code_smell, openai_response):
        for smell in openai_response['smells']:
            if code_smell.smell_type == smell['name']:
                if code_smell.severity == smell['severity']:
                    return True
                else:
                    return False

    @staticmethod
    def view_results(results):
        correct_df = pd.DataFrame(results['correct']).fillna(0).astype(int)
        incorrect_df = pd.DataFrame(results['incorrect']).fillna(0).astype(int)
        print('Correct')
        print(correct_df)
        print('Incorrect')
        print(incorrect_df)


if __name__ == '__main__':
    main = Main()
    results = main.analyze_function_smells(5394, 5433)
    main.view_results(results)
