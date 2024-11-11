from services.smell_analyzer.class_smell_analyzer import ClassSmellAnalyzer
from services.smell_analyzer.function_smell_analyzer import FunctionSmellAnalyzer

if __name__ == '__main__':
    function_analyzer = FunctionSmellAnalyzer()
    function_analyzer.analyze(list(range(5394, 5494)))
    function_analyzer.view_results()
    function_analyzer.view_scores()

    print('\n')

    class_analyzer = ClassSmellAnalyzer()
    class_analyzer.analyze(list(range(5394, 5494)))
    class_analyzer.view_results()
    class_analyzer.view_scores()