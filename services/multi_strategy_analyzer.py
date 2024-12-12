from services.single_strategy_analyzer import SingleStrategyAnalyzer


class MultiStrategyAnalyzer:
    def __init__(self, strategies):
        """
        :param strategies: Dictionary where keys are strategy names and values are assistant IDs
        """
        self.strategies = strategies
        self.results = {}

    def analyze_all_strategies(self, sample_ids):
        for strategy_name, assistant_id in self.strategies.items():
            print(f"Analyzing strategy: {strategy_name}")
            results_file = f'./data/results_{strategy_name}.json'
            analyzer = SingleStrategyAnalyzer(strategy_name, assistant_id, results_file)
            analyzer.analyze_code_samples(sample_ids, use_cached=True)
            self.results[strategy_name] = analyzer.results
            analyzer.binary_evaluation()
            analyzer.ordinal_evaluation()
            analyzer.view_heatmaps()