from services.smell_analyzer.class_smell_analyzer import ClassSmellAnalyzer
from services.smell_analyzer.function_smell_analyzer import FunctionSmellAnalyzer

if __name__ == '__main__':
    function_analyzer = FunctionSmellAnalyzer()
    function_develop_set = function_analyzer.get_develop_set()
    function_analyzer.analyze(function_develop_set)
    function_analyzer.view_results()
    function_analyzer.view_scores()

    print('\n')

    class_analyzer = ClassSmellAnalyzer()
    class_develop_set = class_analyzer.get_develop_set()
    class_analyzer.analyze(class_develop_set)
    class_analyzer.view_results()
    class_analyzer.view_scores()