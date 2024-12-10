import sqlite3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import warnings

from config.config import Config
from data.code_sample import CodeSample
from data.code_smell import CodeSmell
from services.openai_client import OpenAIClient

warnings.filterwarnings("ignore", message=".*tight_layout.*")

SMELL_AMOUNTS = {
    'blob': {'none': 30, 'minor': 5, 'major': 3, 'critical': 2},
    'data class': {'none': 29, 'minor': 5, 'major': 4, 'critical': 2},
    'long method': {'none': 30, 'minor': 5, 'major': 3, 'critical': 2},
    'feature envy': {'none': 34, 'minor': 3, 'major': 2, 'critical': 1}
}

# SMELL_AMOUNTS = {
#     'blob': {'none': 2, 'minor': 1, 'major': 1, 'critical': 1},
#     'data class': {'none': 2, 'minor': 1, 'major': 1, 'critical': 1},
#     'long method': {'none': 2, 'minor': 1, 'major': 1, 'critical': 1},
#     'feature envy': {'none': 2, 'minor': 1, 'major': 1, 'critical': 1}
# }

SMELLS = ['blob', 'data class', 'long method', 'feature envy']
SEVERITIES = ['none', 'minor', 'major', 'critical']


class Analyzer:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_PATH)
        self.openai_client = OpenAIClient(Config.ASSISTANT_ID)
        self.results = {}
        self.initialize_results()
        # self.results = {'blob': {'none': {'total': 3, 'guessed': {'none': 1, 'minor': 0, 'major': 2, 'critical': 0}},
        #                          'minor': {'total': 1, 'guessed': {'none': 0, 'minor': 0, 'major': 1, 'critical': 0}},
        #                          'major': {'total': 1, 'guessed': {'none': 0, 'minor': 0, 'major': 0, 'critical': 1}},
        #                          'critical': {'total': 1,
        #                                       'guessed': {'none': 0, 'minor': 0, 'major': 0, 'critical': 1}}},
        #                 'data class': {
        #                     'none': {'total': 3, 'guessed': {'none': 3, 'minor': 0, 'major': 0, 'critical': 0}},
        #                     'minor': {'total': 1, 'guessed': {'none': 1, 'minor': 0, 'major': 0, 'critical': 0}},
        #                     'major': {'total': 1, 'guessed': {'none': 0, 'minor': 0, 'major': 1, 'critical': 0}},
        #                     'critical': {'total': 1, 'guessed': {'none': 1, 'minor': 0, 'major': 0, 'critical': 0}}},
        #                 'long method': {
        #                     'none': {'total': 4, 'guessed': {'none': 3, 'minor': 1, 'major': 0, 'critical': 0}},
        #                     'minor': {'total': 1, 'guessed': {'none': 0, 'minor': 0, 'major': 1, 'critical': 0}},
        #                     'major': {'total': 1, 'guessed': {'none': 0, 'minor': 0, 'major': 1, 'critical': 0}},
        #                     'critical': {'total': 1, 'guessed': {'none': 1, 'minor': 0, 'major': 0, 'critical': 0}}},
        #                 'feature envy': {
        #                     'none': {'total': 3, 'guessed': {'none': 2, 'minor': 0, 'major': 1, 'critical': 0}},
        #                     'minor': {'total': 1, 'guessed': {'none': 0, 'minor': 1, 'major': 0, 'critical': 0}},
        #                     'major': {'total': 2, 'guessed': {'none': 1, 'minor': 0, 'major': 1, 'critical': 0}},
        #                     'critical': {'total': 1, 'guessed': {'none': 1, 'minor': 0, 'major': 0, 'critical': 0}}}}
        self.results = {'blob': {'none': {'total': 70, 'guessed': {'none': 43, 'minor': 8, 'major': 18, 'critical': 1}},
                                 'minor': {'total': 13, 'guessed': {'none': 0, 'minor': 0, 'major': 13, 'critical': 0}},
                                 'major': {'total': 9, 'guessed': {'none': 0, 'minor': 0, 'major': 9, 'critical': 0}},
                                 'critical': {'total': 6,
                                              'guessed': {'none': 0, 'minor': 0, 'major': 4, 'critical': 2}}},
                        'data class': {
                            'none': {'total': 72, 'guessed': {'none': 36, 'minor': 14, 'major': 22, 'critical': 0}},
                            'minor': {'total': 12, 'guessed': {'none': 4, 'minor': 0, 'major': 8, 'critical': 0}},
                            'major': {'total': 10, 'guessed': {'none': 1, 'minor': 0, 'major': 9, 'critical': 0}},
                            'critical': {'total': 5, 'guessed': {'none': 1, 'minor': 0, 'major': 4, 'critical': 0}}},
                        'long method': {
                            'none': {'total': 52, 'guessed': {'none': 40, 'minor': 8, 'major': 4, 'critical': 0}},
                            'minor': {'total': 14, 'guessed': {'none': 6, 'minor': 2, 'major': 6, 'critical': 0}},
                            'major': {'total': 7, 'guessed': {'none': 2, 'minor': 0, 'major': 5, 'critical': 0}},
                            'critical': {'total': 3, 'guessed': {'none': 2, 'minor': 0, 'major': 1, 'critical': 0}}},
                        'feature envy': {
                            'none': {'total': 58, 'guessed': {'none': 38, 'minor': 9, 'major': 11, 'critical': 0}},
                            'minor': {'total': 8, 'guessed': {'none': 3, 'minor': 1, 'major': 4, 'critical': 0}},
                            'major': {'total': 6, 'guessed': {'none': 5, 'minor': 0, 'major': 1, 'critical': 0}},
                            'critical': {'total': 2, 'guessed': {'none': 2, 'minor': 0, 'major': 0, 'critical': 0}}}}

    def initialize_results(self):
        for smell in SMELLS:
            self.results[smell] = {}
            for severity in SEVERITIES:
                self.results[smell][severity] = {'total': 0,
                                                 'guessed': {'none': 0, 'minor': 0, 'major': 0, 'critical': 0}}

    def run(self, ids=None):
        ids = self.get_ids() if ids is None else [ids]

        # Get distinct code sample ids
        code_sample_ids = CodeSmell.get_code_sample_ids(self.conn, ids)
        print(f'Code sample ids: {code_sample_ids}')
        print(f'Number of code samples: {len(code_sample_ids)}')

        # Calculate the total number of smells
        total_smells = sum(
            len(CodeSample.get_related_smells(self.conn, code_sample_id)) for code_sample_id in code_sample_ids)
        print(f'Number of smells being evaluated: {total_smells}')

        # for code_sample_id in code_sample_ids:
        #     self.process_code_sample(code_sample_id)

        self.view_heatmaps()
        self.binary_evaluation()

    def get_ids(self):
        ids = []
        for smell, severity_amounts in SMELL_AMOUNTS.items():
            for severity, amount in severity_amounts.items():
                ids.extend(CodeSmell.get_ids(self.conn, smell, severity, amount))
        return ids

    def process_code_sample(self, code_sample_id):
        # Get all related smells to the code sample
        smells = CodeSample.get_related_smells(self.conn, code_sample_id)
        sample = CodeSample.get_by_id(self.conn, code_sample_id)
        response = self.openai_client.get_response(sample.code_segment)
        print(f'Code sample id: {code_sample_id}')
        for smell in smells:
            self.update_results(smell, response)
        print(f'Response: {response}')

    def update_results(self, smell, response):
        self.results[smell.smell][smell.severity]['total'] += 1
        print(f'Smell: {smell}')
        smell_is_present = False
        for given_smell in response['smells']:
            if smell.get_name() == given_smell['name'] or (
                    smell.scope == 'class' and given_smell['name'] == 'class') and smell.smell == given_smell['smell']:
                if given_smell['severity'] != 'none':
                    smell_is_present = True
                self.results[smell.smell][smell.severity]['guessed'][given_smell['severity']] += 1
                break

        if not smell_is_present:
            self.results[smell.smell][smell.severity]['guessed']['none'] += 1

    def binary_evaluation(self):
        results_per_smell = {}
        total_tp, total_fp, total_fn, total_tn = 0, 0, 0, 0

        for smell, severity_results in self.results.items():
            tp = 0  # True Positives, i.e. smells correctly identified as present
            fp = 0  # False Positives, i.e. smells getting detected when they are not present
            fn = 0  # False Negatives, i.e. smells not getting detected when they are present
            tn = 0  # True Negatives, i.e. smells correctly identified as not present

            for severity, results in severity_results.items():
                if severity == 'none':
                    fp += sum(results['guessed'][s] for s in ['minor', 'major', 'critical'])
                    tn += results['guessed']['none']
                else:
                    tp += sum(results['guessed'][s] for s in ['minor', 'major', 'critical'])
                    fn += results['guessed']['none']

            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
            f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

            results_per_smell[smell] = {
                'precision': precision,
                'recall': recall,
                'specificity': specificity,
                'f1_score': f1_score
            }

            total_tp += tp
            total_fp += fp
            total_fn += fn
            total_tn += tn

        total_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        total_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        total_specificity = total_tn / (total_tn + total_fp) if (total_tn + total_fp) > 0 else 0
        total_f1_score = 2 * total_precision * total_recall / (total_precision + total_recall) if (
                                                                                                          total_precision + total_recall) > 0 else 0

        print("Per-Smell Metrics:")
        for smell, metrics in results_per_smell.items():
            print(
                f"{smell}: Precision={metrics['precision']:.2f}, Recall={metrics['recall']:.2f}, Specificity={metrics['specificity']:.2f}, F1 Score={metrics['f1_score']:.2f}")

        print("\nTotal Metrics:")
        print(
            f"Precision={total_precision:.2f}, Recall={total_recall:.2f}, Specificity={total_specificity:.2f}, F1 Score={total_f1_score:.2f}")

    def view_heatmaps(self):
        # Create a grid for all heatmaps in a 2x2 layout
        rows = (len(self.results) + 1) // 2  # Calculate required rows for a 2x2 grid
        fig, axes = plt.subplots(rows, 2, figsize=(16, 6 * rows))

        if len(self.results) == 1:
            axes = [[axes[0]] if rows == 1 else axes]  # Handle case for a single heatmap

        axes = axes.flat if len(self.results) > 1 else [axes]  # Flatten axes for easier indexing

        vmin = float('inf')
        vmax = float('-inf')

        # Find the min and max value across all data for shared heatmap scales
        for smell, severity_results in self.results.items():
            for severity, results in severity_results.items():
                vmin = min(vmin, *results['guessed'].values())
                vmax = max(vmax, *results['guessed'].values())

        # Define shared color maps and normalization for the entire figure
        cmap_diag = sns.light_palette("green", as_cmap=True)
        cmap_non_diag = sns.light_palette("red", as_cmap=True)
        norm_diag = plt.Normalize(vmin, vmax)
        norm_non_diag = plt.Normalize(vmin, vmax)

        for ax, (smell, severity_results) in zip(axes, self.results.items()):
            data = []
            for severity, results in severity_results.items():
                data.append(
                    [severity, results['guessed']['none'], results['guessed']['minor'], results['guessed']['major'],
                     results['guessed']['critical']])
            df = pd.DataFrame(data, columns=['Severity', 'None', 'Minor', 'Major', 'Critical'])
            df.set_index('Severity', inplace=True)

            mask = pd.DataFrame(False, index=df.index, columns=df.columns)
            for i, col in enumerate(df.columns):
                if i < len(df.index):
                    mask.iloc[i, i] = True  # Diagonal boxes

            # Plot with shared scales
            sns.heatmap(df, annot=True, cmap=cmap_diag, fmt='d', linewidths=.5, ax=ax, mask=~mask,
                        cbar=False, vmin=vmin, vmax=vmax, norm=norm_diag)
            sns.heatmap(df, annot=True, cmap=cmap_non_diag, fmt='d', linewidths=.5, ax=ax, mask=mask,
                        cbar=False, vmin=vmin, vmax=vmax, norm=norm_non_diag)

            ax.set_title(f'{smell.capitalize()} Results Heatmap')
            ax.set_ylabel('Actual Severity')
            ax.set_xlabel('Guessed Severity')

        # Create only one colorbar showing ranges for the entire figure
        cbar_ax = fig.add_axes([0.93, 0.15, 0.02, 0.7])
        sm = plt.cm.ScalarMappable(cmap=sns.light_palette("green", as_cmap=True), norm=norm_diag)
        sm_non_diag = plt.cm.ScalarMappable(cmap=sns.light_palette("red", as_cmap=True), norm=norm_non_diag)
        fig.colorbar(sm, cax=cbar_ax, label="Correct Answers")

        # Add label for incorrect answers
        cbar_ax_non_diag = fig.add_axes([0.88, 0.15, 0.02, 0.7])
        fig.colorbar(sm_non_diag, cax=cbar_ax_non_diag, label="Incorrect Answers")

        # Remove unused subplots if necessary
        for ax in axes[len(self.results):]:
            fig.delaxes(ax)

        plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust layout to make space for the colorbars
        plt.show()
