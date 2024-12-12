import sqlite3

from config.config import Config
from data.code_smell import CodeSmell
from services.multi_strategy_analyzer import MultiStrategyAnalyzer
from services.single_strategy_analyzer import SingleStrategyAnalyzer

SMELL_AMOUNTS = {
    'blob': {'none': 30, 'minor': 5, 'major': 3, 'critical': 2},
    'data class': {'none': 29, 'minor': 5, 'major': 4, 'critical': 2},
    'long method': {'none': 30, 'minor': 5, 'major': 3, 'critical': 2},
    'feature envy': {'none': 34, 'minor': 3, 'major': 2, 'critical': 1}
}

# SMELL_AMOUNTS = {
#     'blob': {'none': 15, 'minor': 2, 'major': 2, 'critical': 1},
#     'data class': {'none': 14, 'minor': 3, 'major': 2, 'critical': 1},
#     'long method': {'none': 15, 'minor': 2, 'major': 2, 'critical': 1},
#     'feature envy': {'none': 17, 'minor': 1, 'major': 1, 'critical': 1}
# }

def get_smell_ids(conn, smell_amounts):
    ids = []
    for smell, severity_amounts in smell_amounts.items():
        for severity, amount in severity_amounts.items():
            ids.extend(CodeSmell.get_ids(conn, smell, severity, amount))
    return ids

if __name__ == '__main__':
    conn = sqlite3.connect(Config.DB_PATH)
    smell_ids = get_smell_ids(conn, SMELL_AMOUNTS)
    code_sample_ids = CodeSmell.get_code_sample_ids(conn, smell_ids)
    print(f'Code sample ids: {code_sample_ids}')
    print(f'Number of code samples: {len(code_sample_ids)}')

    strategies = Config.PROMPT_STRATEGIES

    # multi_analyzer = MultiStrategyAnalyzer(strategies)
    # multi_analyzer.analyze_all_strategies(code_sample_ids)

    strategy = 'zero-shot'
    single_analyzer = SingleStrategyAnalyzer(strategy, strategies[strategy], f'./data/results_{strategy}.json')
    single_analyzer.analyze_code_samples(code_sample_ids, use_cached=True)
    single_analyzer.binary_evaluation()
    single_analyzer.ordinal_evaluation()
    single_analyzer.view_heatmaps()
    conn.close()