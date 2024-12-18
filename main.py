import sqlite3

from config.config import Config
from data.code_smell import CodeSmell
from services.multi_strategy_analyzer import MultiStrategyAnalyzer
from services.single_strategy_analyzer import SingleStrategyAnalyzer

def get_smell_ids(conn, smell_amounts, min_id = 0):
    ids = []
    for smell, severity_amounts in smell_amounts.items():
        for severity, amount in severity_amounts.items():
            ids.extend(CodeSmell.get_ids(conn, smell, severity, amount, min_id))
    return sorted(ids)

def iterative_strategy_improvement(strategy):
    smell_amounts = {
        'blob': {'none': 41, 'minor': 5, 'major': 3, 'critical': 1},
        'data class': {'none': 40, 'minor': 4, 'major': 4, 'critical': 2},
        'long method': {'none': 43, 'minor': 3, 'major': 3, 'critical': 1},
        'feature envy': {'none': 45, 'minor': 3, 'major': 1, 'critical': 1}
    }
    smell_ids = get_smell_ids(conn, smell_amounts)
    print(f'Smell ids: {smell_ids}')
    code_sample_ids = CodeSmell.get_code_sample_ids(conn, smell_ids)
    print(f'Code sample ids: {code_sample_ids}')
    print(f'Number of code samples: {len(code_sample_ids)}')
    single_analyzer = SingleStrategyAnalyzer(strategy, Config.PROMPT_STRATEGIES[strategy], f'./data/results_{strategy}.json')
    single_analyzer.analyze_code_samples(code_sample_ids, False)
    single_analyzer.binary_evaluation()
    single_analyzer.ordinal_evaluation()
    single_analyzer.view_heatmaps(title=f'Results Heatmaps ({strategy})')

def analysis():
    smell_amounts = {
        'blob': {'none': 83, 'minor': 10, 'major': 5, 'critical': 2},
        'data class': {'none': 81, 'minor': 8, 'major': 8, 'critical': 3},
        'long method': {'none': 87, 'minor': 7, 'major': 5, 'critical': 1},
        'feature envy': {'none': 90, 'minor': 6, 'major': 3, 'critical': 1}
    }
    min_smell_id = 2739
    smell_ids = get_smell_ids(conn, smell_amounts, min_smell_id)
    print(f'Smell ids: {smell_ids}')
    code_sample_ids = CodeSmell.get_code_sample_ids(conn, smell_ids)
    print(f'Code sample ids: {code_sample_ids}')
    print(f'Number of code samples: {len(code_sample_ids)}')
    strategies = Config.PROMPT_STRATEGIES
    multi_analyzer = MultiStrategyAnalyzer(strategies, min_id=min_smell_id)
    multi_analyzer.analyze_all_strategies(code_sample_ids)


if __name__ == '__main__':
    conn = sqlite3.connect(Config.DB_PATH)
    iterative_strategy_improvement('zero-shot')

    conn.close()