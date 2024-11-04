from services.smell_analyzer.class_smell_analyzer import ClassSmellAnalyzer
from services.smell_analyzer.function_smell_analyzer import FunctionSmellAnalyzer

if __name__ == '__main__':
    function_analyzer = FunctionSmellAnalyzer()
    function_analyzer.analyze(5394, 5433)
    function_analyzer.view_results()

    class_analyzer = ClassSmellAnalyzer()
    class_analyzer.analyze(5394, 5433)
    class_analyzer.view_results()