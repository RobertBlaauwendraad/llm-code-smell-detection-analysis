from config.config import Config
from services.multi_strategy_analyzer import MultiStrategyAnalyzer

if __name__ == '__main__':
    strategies = Config.PROMPT_STRATEGIES
    multi_analyzer = MultiStrategyAnalyzer(strategies)
    multi_analyzer.analyze_all_strategies()
