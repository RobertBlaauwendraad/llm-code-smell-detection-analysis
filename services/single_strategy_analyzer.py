import json
import os
import sqlite3

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import warnings

from config.config import Config
from data.code_sample import CodeSample
from services.openai_client import OpenAIClient

warnings.filterwarnings("ignore", message=".*tight_layout.*")

SMELLS = ['blob', 'data class', 'long method', 'feature envy']
SEVERITIES = ['none', 'minor', 'major', 'critical']


class SingleStrategyAnalyzer:
    def __init__(self, strategy_name, assistant_id, results_file):
        self.strategy_name = strategy_name
        self.assistant_id = assistant_id
        self.results_file = results_file
        self.conn = sqlite3.connect(Config.DB_PATH)
        self.openai_client = OpenAIClient(assistant_id)
        self.results = self.initialize_results()

    @staticmethod
    def initialize_results():
        return {
            smell: {severity: {'total': 0, 'guessed': {sev: 0 for sev in SEVERITIES}}
                    for severity in SEVERITIES}
            for smell in SMELLS
        }

    def save_results(self):
        with open(self.results_file, "w") as file:
            json.dump(self.results, file)
        print(f"Results saved to {self.results_file}")

    def load_results(self):
        if os.path.exists(self.results_file):
            with open(self.results_file, "r") as file:
                self.results = json.load(file)
            print(f"Results loaded from {self.results_file}")
        else:
            print(f"Results file {self.results_file} not found. Starting fresh.")
            self.initialize_results()

    def analyze_code_samples(self, code_sample_ids, use_cached=False):
        if use_cached:
            if os.path.exists(self.results_file):
                self.load_results()
                return
            else:
                print(f"Cached file {self.results_file} not found. Generating new results.")

        for code_sample_id in code_sample_ids:
            self.process_code_sample(code_sample_id)

        self.save_results()

    def process_code_sample(self, code_sample_id):
        smells = CodeSample.get_related_smells(self.conn, code_sample_id)
        sample = CodeSample.get_by_id(self.conn, code_sample_id)
        response = self.openai_client.get_response(sample.code_segment)
        for smell in smells:
            self.update_results(smell, response)

    def update_results(self, smell, response):
        self.results[smell.smell][smell.severity]['total'] += 1
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

        print("\nBinary Classification Metrics:")
        for smell, metrics in results_per_smell.items():
            print(
                f"{smell}: Precision={metrics['precision']:.2f}, Recall={metrics['recall']:.2f}, Specificity={metrics['specificity']:.2f}, F1 Score={metrics['f1_score']:.2f}")

        print(
            f"\nCombined: Precision={total_precision:.2f}, Recall={total_recall:.2f}, Specificity={total_specificity:.2f}, F1 Score={total_f1_score:.2f}")

    def ordinal_evaluation(self):
        """
        Calculate and print Weighted Kappa for each smell type, including a combined QWK/WK.
        """
        print("\nWeighted Kappa Metrics:")
        # Initialize combined results matrix
        combined_results = {severity: {'total': 0, 'guessed': {sev: 0 for sev in SEVERITIES}} for severity in
                            SEVERITIES}

        # Aggregate results across all smells
        for smell, severity_results in self.results.items():
            for severity, results in severity_results.items():
                combined_results[severity]['total'] += results['total']
                for guessed, count in results['guessed'].items():
                    combined_results[severity]['guessed'][guessed] += count

        # Per-smell metrics
        for smell, severity_results in self.results.items():
            kappa_quadratic = self.weighted_kappa(severity_results, weights='quadratic')
            kappa_linear = self.weighted_kappa(severity_results, weights='linear')
            print(f"{smell}: Quadratic Weighted Kappa={kappa_quadratic:.2f}, Linear Weighted Kappa={kappa_linear:.2f}")

        # Combined metrics
        combined_kappa_quadratic = self.weighted_kappa(combined_results, weights='quadratic')
        combined_kappa_linear = self.weighted_kappa(combined_results, weights='linear')
        print(
            f"\nCombined: Quadratic Weighted Kappa={combined_kappa_quadratic:.2f}, Linear Weighted Kappa={combined_kappa_linear:.2f}")

    def weighted_kappa(self, severity_results, weights='linear'):
        """
        Calculate Weighted Kappa for a specific smell, excluding 'none' cases.

        :param severity_results: A dictionary with 'total' and 'guessed' for each severity.
        :param weights: 'linear' or 'quadratic' to determine weight matrix type.
        :return: Weighted Kappa score.
        """
        n = len(SEVERITIES) - 1  # Exclude 'none'
        valid_severities = SEVERITIES[1:]  # Skip 'none'

        # Observed matrix
        observed = np.zeros((n, n))
        for i, actual in enumerate(valid_severities):
            for j, guessed in enumerate(valid_severities):
                observed[i, j] = severity_results[actual]['guessed'][guessed]

        # Normalize observed matrix
        total_observed = observed.sum()
        observed /= total_observed

        # Marginal probabilities
        actual_totals = observed.sum(axis=1)
        predicted_totals = observed.sum(axis=0)

        # Expected matrix
        expected = np.outer(actual_totals, predicted_totals)

        # Weight matrix
        weight_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                diff = abs(i - j)
                if weights == 'linear':
                    weight_matrix[i, j] = diff
                elif weights == 'quadratic':
                    weight_matrix[i, j] = diff ** 2

        # Normalize weight matrix
        weight_matrix /= weight_matrix.max()

        # Calculate weighted kappa
        observed_disagreement = (observed * weight_matrix).sum()
        expected_disagreement = (expected * weight_matrix).sum()
        kappa = 1 - (observed_disagreement / expected_disagreement if expected_disagreement > 0 else 1)

        return kappa

    def view_heatmaps(self, title='Results Heatmaps'):
        # Create a grid for all heatmaps in a 2x2 layout
        rows = (len(self.results) + 1) // 2  # Calculate required rows for a 2x2 grid
        fig, axes = plt.subplots(rows, 2, figsize=(16, 6 * rows))

        if len(self.results) == 1:
            axes = [[axes[0]] if rows == 1 else axes]  # Handle case for a single heatmap

        axes = axes.flat if len(self.results) > 1 else [axes]  # Flatten axes for easier indexing

        vmin = float('inf')
        vmax = float('-inf')

        # Find the min and max value for non-diagonal (incorrect) data
        for smell, severity_results in self.results.items():
            for severity, results in severity_results.items():
                for guessed_severity, value in results['guessed'].items():
                    if severity != guessed_severity:
                        vmin = min(vmin, value)
                        vmax = max(vmax, value)

        # Define shared color maps and normalization for the entire figure
        cmap_diag = sns.light_palette("green", as_cmap=True)
        cmap_non_diag = sns.light_palette("red", as_cmap=True)
        norm_diag = plt.Normalize(0, 1)  # Percentage range for correct answers
        norm_non_diag = plt.Normalize(vmin, vmax)

        for ax, (smell, severity_results) in zip(axes, self.results.items()):
            data = []
            annotations = []  # Store annotations for each cell
            for severity, results in severity_results.items():
                row = [severity]
                row_annotations = [""]
                for guessed_severity in ['none', 'minor', 'major', 'critical']:
                    guessed = results['guessed'][guessed_severity]
                    if severity == guessed_severity:
                        total = results['total']
                        percentage = guessed / total if total > 0 else 0
                        row.append(percentage)  # Use percentage for diagonal cells
                        row_annotations.append(f"{guessed}/{total}" if total > 0 else "0/0")  # Correct/total
                    else:
                        row.append(guessed)  # Use absolute values for non-diagonal
                        row_annotations.append(str(guessed))
                data.append(row[1:])  # Skip severity name for heatmap data
                annotations.append(row_annotations[1:])  # Skip severity name for annotations

            df = pd.DataFrame(data, columns=['None', 'Minor', 'Major', 'Critical'])
            df.index = ['None', 'Minor', 'Major', 'Critical']

            mask = pd.DataFrame(False, index=df.index, columns=df.columns)
            for i, col in enumerate(df.columns):
                if i < len(df.index):
                    mask.iloc[i, i] = True  # Diagonal boxes

            # Plot with shared scales
            sns.heatmap(df, annot=False, cmap=cmap_diag, fmt='d', linewidths=.5, ax=ax, mask=~mask,
                        cbar=False, vmin=0, vmax=1, norm=norm_diag)  # Diagonal uses percentage normalization
            sns.heatmap(df, annot=False, cmap=cmap_non_diag, fmt='d', linewidths=.5, ax=ax, mask=mask,
                        cbar=False, vmin=vmin, vmax=vmax, norm=norm_non_diag)

            # Add annotations to the heatmap
            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    ax.text(j + 0.5, i + 0.5, annotations[i][j],
                            ha="center", va="center", color="black")

            ax.set_title(f'{smell.capitalize()}')
            ax.set_ylabel('Actual Severity')
            ax.set_xlabel('Guessed Severity')

        # Create only one colorbar showing ranges for the entire figure
        cbar_ax = fig.add_axes([0.93, 0.15, 0.02, 0.7])
        sm = plt.cm.ScalarMappable(cmap=sns.light_palette("green", as_cmap=True), norm=norm_diag)
        sm_non_diag = plt.cm.ScalarMappable(cmap=sns.light_palette("red", as_cmap=True), norm=norm_non_diag)
        fig.colorbar(sm, cax=cbar_ax, label="Percentage Correct (Diagonal)")

        # Add label for incorrect answers
        cbar_ax_non_diag = fig.add_axes([0.88, 0.15, 0.02, 0.7])
        fig.colorbar(sm_non_diag, cax=cbar_ax_non_diag, label="Incorrect Answers")

        # Remove unused subplots if necessary
        for ax in axes[len(self.results):]:
            fig.delaxes(ax)

        plt.tight_layout(rect=[0, 0, 0.85, 0.95])  # Adjust layout to make space
        plt.subplots_adjust(top=0.94)  # Add more whitespace on top
        plt.suptitle(title, fontsize=16, fontweight='bold')  # Move title higher
        plt.show()
