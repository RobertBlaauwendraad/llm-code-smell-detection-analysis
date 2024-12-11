from config.config import Config
from services.analyzer import Analyzer

if __name__ == '__main__':
    analyzer = Analyzer()
    strategies = Config.PROMPT_STRATEGIES
    analyzer.strategy_analysis(strategies)
    # analyzer.run(use_cached=True)
    # analyzer.view_heatmaps()
    # analyzer.binary_evaluation()
    # analyzer.ordinal_evaluation()
