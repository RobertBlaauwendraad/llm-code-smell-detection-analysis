import sqlite3

from config.config import Config
from data.code_smell import CodeSmell
from services.single_strategy_analyzer import SingleStrategyAnalyzer

# SMELL_AMOUNTS = {
#     'blob': {'none': 30, 'minor': 5, 'major': 3, 'critical': 2},
#     'data class': {'none': 29, 'minor': 5, 'major': 4, 'critical': 2},
#     'long method': {'none': 30, 'minor': 5, 'major': 3, 'critical': 2},
#     'feature envy': {'none': 34, 'minor': 3, 'major': 2, 'critical': 1}
# }

SMELL_AMOUNTS = {
    'blob': {'none': 15, 'minor': 2, 'major': 2, 'critical': 1},
    'data class': {'none': 14, 'minor': 3, 'major': 2, 'critical': 1},
    'long method': {'none': 15, 'minor': 2, 'major': 2, 'critical': 1},
    'feature envy': {'none': 17, 'minor': 1, 'major': 1, 'critical': 1}
}


class MultiStrategyAnalyzer:
    def __init__(self, strategies):
        """
        :param strategies: Dictionary where keys are strategy names and values are assistant IDs
        """
        self.strategies = strategies
        self.results = {}

    def analyze_all_strategies(self, ids=None):
        ids = self.get_ids() if ids is None else ids

        for strategy_name, assistant_id in self.strategies.items():
            print(f"Analyzing strategy: {strategy_name}")
            results_file = f'./data/results_{strategy_name}.json'
            analyzer = SingleStrategyAnalyzer(strategy_name, assistant_id, results_file)
            analyzer.analyze_code_samples(ids, use_cached=True)
            self.results[strategy_name] = analyzer.results
            analyzer.binary_evaluation()
            analyzer.ordinal_evaluation()

    def get_ids(self):
        ids = []
        for smell, severity_amounts in SMELL_AMOUNTS.items():
            for severity, amount in severity_amounts.items():
                ids.extend(CodeSmell.get_ids(sqlite3.connect(Config.DB_PATH), smell, severity, amount))
        return ids
