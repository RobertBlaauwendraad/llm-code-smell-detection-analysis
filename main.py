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

def get_all_smell_ids(conn, excluded_ids=None):
    all_ids = CodeSmell.get_all_ids(conn)
    if excluded_ids:
        return [id for id in all_ids if id not in excluded_ids]
    return all_ids


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


def big_analysis():
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
    excluded_smells = excluded_smells + [742, 743, 760, 761, 8593, 8594, 768, 769, 772, 773, 782, 783, 794, 795, 796,
                                         797, 810, 811, 816, 817, 812, 813, 814, 815, 818, 819, 820, 821, 822, 823, 826,
                                         827, 830, 831, 834, 835, 836, 837, 838, 839, 842, 843, 844, 845, 846, 847, 848,
                                         851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 868,
                                         869, 870, 871, 872, 873, 874, 875, 10177, 10178, 876, 877, 878, 879, 882, 883,
                                         5538, 5539, 886, 887, 888, 889, 890, 891, 894, 895, 896, 897, 920, 921, 934,
                                         935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 952,
                                         953, 954, 955, 956, 957, 974, 975, 976, 977, 978, 979, 984, 985, 986, 987, 990,
                                         991, 992, 993, 996, 997, 998, 999, 1000, 1001, 4599, 4600, 1002, 1003, 1004,
                                         1005, 10165, 10166, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015,
                                         7967, 7968, 1016, 1017, 1018, 1019, 1020, 1021, 1072, 1073, 10163, 10164, 1022,
                                         1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035,
                                         1036, 1037, 1038, 1039, 1042, 1043, 1044, 1045, 1046, 1047, 4250, 4251, 10129,
                                         10130, 1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057, 1058, 1059,
                                         1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067, 1068, 1069, 1070, 1071, 1074,
                                         1075, 1076, 1077, 1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087,
                                         1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097, 1098, 1099, 1100,
                                         1101, 1102, 1103, 1104, 1105, 1106, 1107, 1108, 1109, 1110, 1111, 1112, 1113,
                                         1114, 1115, 1116, 1117, 1118, 1119, 1120, 1121, 1124, 1125, 1126, 1127, 1128,
                                         1129, 4469, 4470, 1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139,
                                         1140, 1141, 1142, 1143, 1144, 1145, 1162, 1163, 1146, 1147, 1148, 1149, 1150,
                                         1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159, 1160, 1161, 1164, 1165,
                                         1166, 1167, 1168, 1169, 1170, 1171, 1172, 1173, 1174, 1175, 1176, 1177, 1178,
                                         1179, 1180, 1181, 1182, 1183, 1184, 1185, 1212, 1213, 1186, 1187, 1188, 1189,
                                         1190, 1191, 1192, 1193, 1196, 1197, 1198, 1199, 1200, 1201, 1202, 1203, 1204,
                                         1205, 1206, 1207, 1208, 1209, 1210, 1211, 1214, 1215, 1216, 1217, 1218, 1219,
                                         1220, 1221, 1222, 1223, 1224, 1225, 1228, 1229, 1230, 1231, 1240, 1241, 1242,
                                         1243, 1248, 1249, 1253, 1254, 1255, 1256, 1259, 1260, 1261, 1262, 1268, 1269,
                                         1272, 1273, 1274, 1275, 1278, 1279, 1292, 1293, 1294, 1295, 1302, 1303, 1304,
                                         1305, 1306, 1307, 1308, 1309, 1310, 1311, 1314, 1315, 1316, 1317, 1320, 1321,
                                         1324, 1325, 1330, 1331, 1338, 1339, 1348, 1349, 1354, 1355, 1356, 1357, 1358,
                                         1359, 1360, 1361, 1370, 1371, 1372, 1373, 1378, 1379, 1391, 1392, 1395, 1396,
                                         1463, 1464, 1499, 1500, 1509, 1510, 1513, 1514, 1607, 1608, 1673, 1674, 2195,
                                         2196, 2253, 2254, 2737, 2738]
    excluded_smells = excluded_smells + [2960, 2961, 7529, 7530]
    smell_ids = get_all_smell_ids(conn, excluded_smells)
    print(f'Smell ids: {smell_ids}')
    code_sample_ids = CodeSmell.get_code_sample_ids(conn, smell_ids)
    print(f'Code sample ids: {code_sample_ids}')
    print(f'Number of code samples: {len(code_sample_ids)}')
    strategy = 'chain-of-thought'
    single_analyzer = SingleStrategyAnalyzer(strategy, Config.PROMPT_STRATEGIES[strategy],
                                             f'./data/results_big_{strategy}.json')
    single_analyzer.analyze_code_samples(code_sample_ids, True)
    single_analyzer.binary_evaluation()
    single_analyzer.ordinal_evaluation()
    single_analyzer.view_heatmaps(title=f'Results Heatmaps ({strategy})')


if __name__ == '__main__':
    conn = sqlite3.connect(Config.DB_PATH)
    # iterative_strategy_improvement('zero-shot')
    # analysis()
    big_analysis()

    conn.close()
