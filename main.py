from services.smell_analyzer.class_smell_analyzer import ClassSmellAnalyzer
from services.smell_analyzer.combined_smell_analyzer import CombinedSmellAnalyzer
from services.smell_analyzer.function_smell_analyzer import FunctionSmellAnalyzer

if __name__ == '__main__':
    function_analyzer = FunctionSmellAnalyzer()
    function_develop_set = function_analyzer.get_develop_set()
    function_analyzer.analyze(function_develop_set)
    function_analyzer.view_results()
    function_analyzer.view_scores()
    function_analyzer.weighted_kappa()
    function_analyzer.quadratic_weighted_kappa()


    print('\n')

    class_analyzer = ClassSmellAnalyzer()
    class_develop_set = class_analyzer.get_develop_set()
    class_analyzer.analyze(class_develop_set)
    class_analyzer.view_results()
    class_analyzer.view_scores()

    print('\n')

    combined_analyzer = CombinedSmellAnalyzer()
    combined_develop_set = combined_analyzer.get_develop_set()
    combined_analyzer.analyze(combined_develop_set)
    combined_analyzer.view_results()
    combined_analyzer.view_scores()
