import sqlite3

import pandas as pd

from config.config import Config
from services.openai_client import OpenAIClient


class BaseSmellAnalyzer:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_PATH)
        self.client = OpenAIClient()
        self.results = {}

    @staticmethod
    def compare_results(code_smell, openai_response):
        # If the code smell is not present, the response should not contain it
        if code_smell.severity == 'none':
            for smell in openai_response['smells']:
                if code_smell.smell_type == smell['name']:
                    return False
            return True

        # If the code smell is present, the response should contain it with the same severity
        for smell in openai_response['smells']:
            if code_smell.smell_type == smell['name']:
                if code_smell.severity == smell['severity']:
                    return True
                else:
                    return False

    def count_results(self, openai_response, scope, smells):
        for smell in smells:
            if smell.code_sample_id == scope.sample_id:
                if smell.smell_type not in self.results:
                    self.results[smell.smell_type] = {'none': {'correct': 0, 'total': 0},
                                                      'minor': {'correct': 0, 'total': 0},
                                                      'major': {'correct': 0, 'total': 0},
                                                      'critical': {'correct': 0, 'total': 0}}
                self.results[smell.smell_type][smell.severity]['total'] += 1
                if self.compare_results(smell, openai_response):
                    self.results[smell.smell_type][smell.severity]['correct'] += 1

    def view_results(self):
        data = {}
        for smell_type, severity in self.results.items():
            data[smell_type] = []
            for severity, results in severity.items():
                data[smell_type].append(f'{results["correct"]}/{results["total"]}')

        df = pd.DataFrame(data, index=['None', 'Minor', 'Major', 'Critical'])

        # Calculate totals
        total_row = []
        for smell_type in data.keys():
            total_correct = sum(int(results.split('/')[0]) for results in data[smell_type])
            total_total = sum(int(results.split('/')[1]) for results in data[smell_type])
            total_row.append(f'{total_correct}/{total_total}')

        df.loc['Total'] = total_row
        print(df)

    def view_scores(self):
        for smell_type, severities in self.results.items():
            true_positive = sum(results['correct'] for severity, results in severities.items() if severity != 'none')
            false_positive = sum(results['total'] - results['correct'] for severity, results in severities.items() if severity != 'none')
            true_negative = severities['none']['correct']
            false_negative = severities['none']['total'] - severities['none']['correct']

            self.results[smell_type]['true_positive'] = true_positive
            self.results[smell_type]['false_positive'] = false_positive
            self.results[smell_type]['true_negative'] = true_negative
            self.results[smell_type]['false_negative'] = false_negative

            accuracy = (true_positive + true_negative) / (true_positive + false_positive + true_negative + false_negative)
            precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
            recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            self.results[smell_type]['accuracy'] = accuracy
            self.results[smell_type]['precision'] = precision
            self.results[smell_type]['recall'] = recall
            self.results[smell_type]['f1_score'] = f1_score

        metrics = {smell_type: {metric: values[metric] for metric in ['accuracy', 'precision', 'recall', 'f1_score']}
                   for smell_type, values in self.results.items()}

        df = pd.DataFrame(metrics)
        print(df)