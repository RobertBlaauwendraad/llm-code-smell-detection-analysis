import sqlite3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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
                    self.results[smell.smell_type] = {'none': {'correct': 0, 'total': 0, 'guesses': {'none': 0, 'minor': 0, 'major': 0, 'critical': 0}},
                                                      'minor': {'correct': 0, 'total': 0, 'guesses': {'none': 0, 'minor': 0, 'major': 0, 'critical': 0}},
                                                      'major': {'correct': 0, 'total': 0, 'guesses': {'none': 0, 'minor': 0, 'major': 0, 'critical': 0}},
                                                      'critical': {'correct': 0, 'total': 0, 'guesses': {'none': 0, 'minor': 0, 'major': 0, 'critical': 0}}}
                self.results[smell.smell_type][smell.severity]['total'] += 1
                guessed_severity = 'none'
                for smell_response in openai_response['smells']:
                    if smell.smell_type == smell_response['name']:
                        guessed_severity = smell_response['severity']
                        break
                self.results[smell.smell_type][smell.severity]['guesses'][guessed_severity] += 1
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

    def weighted_kappa(self):
        observed = np.zeros((4, 4))
        expected = np.zeros((4, 4))
        weights = np.zeros((4, 4))
        severity_levels = ['none', 'minor', 'major', 'critical']

        # Populate the observed matrix
        for smell_type, severities in self.results.items():
            for i, severity in enumerate(severity_levels):
                for j, other_severity in enumerate(severity_levels):
                    observed[i, j] += severities[severity]['guesses'][other_severity]

        total = np.sum(observed)
        if total == 0:
            print("No data to calculate Weighted Kappa")
            return

        # Normalize observed matrix
        observed = observed / total

        # Calculate expected matrix
        row_totals = np.sum(observed, axis=1)
        col_totals = np.sum(observed, axis=0)
        for i in range(4):
            for j in range(4):
                expected[i, j] = row_totals[i] * col_totals[j]

        # Calculate weights matrix
        for i in range(4):
            for j in range(4):
                weights[i, j] = 1 - ((i - j) ** 2 / (3 ** 2))  # Max difference is 3 (critical vs none)

        # Calculate weighted kappa
        weighted_observed = np.sum(weights * observed)
        weighted_expected = np.sum(weights * expected)

        kappa = (weighted_observed - weighted_expected) / (1 - weighted_expected) if (1 - weighted_expected) != 0 else 0

        print("Observed Matrix:")
        print(pd.DataFrame(observed, columns=severity_levels, index=severity_levels))
        print("\nExpected Matrix:")
        print(pd.DataFrame(expected, columns=severity_levels, index=severity_levels))
        print("\nWeights Matrix:")
        print(pd.DataFrame(weights, columns=severity_levels, index=severity_levels))
        print(f'\nWeighted Kappa: {kappa:.4f}')

        # Visualize the matrices using heatmaps
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        sns.heatmap(observed, annot=True, fmt=".2f", cmap="YlGnBu", ax=axes[0], xticklabels=severity_levels, yticklabels=severity_levels)
        axes[0].set_title('Observed Matrix')
        sns.heatmap(expected, annot=True, fmt=".2f", cmap="YlGnBu", ax=axes[1], xticklabels=severity_levels, yticklabels=severity_levels)
        axes[1].set_title('Expected Matrix')
        sns.heatmap(weights, annot=True, fmt=".2f", cmap="YlGnBu", ax=axes[2], xticklabels=severity_levels, yticklabels=severity_levels)
        axes[2].set_title('Weights Matrix')

        plt.tight_layout()
        plt.show()

        return kappa

    def quadratic_weighted_kappa(self):
        observed = np.zeros((4, 4))
        severity_levels = ['none', 'minor', 'major', 'critical']

        # Populate the observed matrix
        for smell_type, severities in self.results.items():
            for i, severity in enumerate(severity_levels):
                for j, other_severity in enumerate(severity_levels):
                    observed[i, j] += severities[severity]['guesses'][other_severity]

        total = np.sum(observed)
        if total == 0:
            print("No data to calculate Quadratic Weighted Kappa")
            return

        # Normalize observed matrix
        observed = observed / total

        # Calculate weights matrix
        weights = np.zeros((4, 4))
        for i in range(4):
            for j in range(4):
                weights[i, j] = (i - j) ** 2

        # Calculate quadratic weighted kappa
        numerator = 0
        denominator = 0
        for i in range(4):
            for j in range(4):
                numerator += weights[i, j] * observed[i, j]
                denominator += weights[i, j] * (i - j) ** 2

        kappa = 1 - (numerator / denominator) if denominator != 0 else 0

        print("Observed Matrix:")
        print(pd.DataFrame(observed, columns=severity_levels, index=severity_levels))
        print("\nWeights Matrix:")
        print(pd.DataFrame(weights, columns=severity_levels, index=severity_levels))
        print(f'\nQuadratic Weighted Kappa: {kappa:.4f}')

        # Visualize the matrices using heatmaps
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        sns.heatmap(observed, annot=True, fmt=".2f", cmap="YlGnBu", ax=axes[0], xticklabels=severity_levels, yticklabels=severity_levels)
        axes[0].set_title('Observed Matrix')
        sns.heatmap(weights, annot=True, fmt=".2f", cmap="YlGnBu", ax=axes[1], xticklabels=severity_levels, yticklabels=severity_levels)
        axes[1].set_title('Weights Matrix')

        plt.tight_layout()
        plt.show()

        return kappa