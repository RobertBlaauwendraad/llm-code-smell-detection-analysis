from services.smell_analyzer.class_smell_analyzer import ClassSmellAnalyzer
from services.smell_analyzer.function_smell_analyzer import FunctionSmellAnalyzer

if __name__ == '__main__':
    function_analyzer = FunctionSmellAnalyzer()
    function_analyzer.analyze(5394, 5493)
    function_analyzer.view_results()

    print('\n')

    class_analyzer = ClassSmellAnalyzer()
    class_analyzer.analyze(5394, 5493)
    class_analyzer.view_results()