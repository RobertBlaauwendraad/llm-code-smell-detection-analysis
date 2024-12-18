import sqlite3

from config.config import Config
from data.code_smell import CodeSmell
from services.multi_strategy_analyzer import MultiStrategyAnalyzer
from services.single_strategy_analyzer import SingleStrategyAnalyzer


def get_smell_ids(conn, smell_amounts, excluded_ids=None):
    ids = []
    for smell, severity_amounts in smell_amounts.items():
        for severity, amount in severity_amounts.items():
            ids.extend(CodeSmell.get_ids(conn, smell, severity, amount, excluded_ids))
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
    single_analyzer = SingleStrategyAnalyzer(strategy, Config.PROMPT_STRATEGIES[strategy],
                                             f'./data/results_{strategy}.json')
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
    excluded_smells = [526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544,
                       545, 546, 547, 548, 549, 552, 553, 554, 555, 556, 557, 558, 559, 562, 563, 564, 565, 10217,
                       10218, 566, 567, 568, 569, 570, 571, 10149, 10150, 572, 573, 574, 575, 576, 577, 578, 579, 580,
                       581, 582, 583, 586, 587, 588, 589, 590, 591, 592, 593, 596, 597, 598, 599, 600, 601, 602, 603,
                       604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622,
                       623, 624, 625, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 650, 651, 652, 653,
                       654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 3621, 3622, 5424, 5425, 666, 667, 668, 669,
                       670, 671, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 686, 687, 688, 689, 690, 691, 692,
                       693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 714, 715,
                       716, 717, 718, 719, 720, 721, 2867, 2868, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732,
                       733, 736, 737, 738, 739, 740, 741, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755,
                       756, 757, 758, 759, 762, 763, 764, 765, 766, 767, 776, 777, 778, 779, 800, 801, 804, 805, 808,
                       809, 832, 833, 840, 841, 866, 867, 988, 989, 1122, 1123, 1263]
    smell_ids = get_smell_ids(conn, smell_amounts, excluded_smells)
    print(f'Smell ids: {smell_ids}')
    code_sample_ids = CodeSmell.get_code_sample_ids(conn, smell_ids)
    print(f'Code sample ids: {code_sample_ids}')
    print(f'Number of code samples: {len(code_sample_ids)}')
    strategies = Config.PROMPT_STRATEGIES
    multi_analyzer = MultiStrategyAnalyzer(strategies)
    multi_analyzer.analyze_all_strategies(code_sample_ids)


if __name__ == '__main__':
    conn = sqlite3.connect(Config.DB_PATH)
    # iterative_strategy_improvement('role_prompting')
    analysis()

    conn.close()
