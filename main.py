from services.smell_analyzer import SmellAnalyzer

if __name__ == '__main__':
    analyzer = SmellAnalyzer()
    results = analyzer.analyze_function_smells(5394, 5433)
    analyzer.view_results(results)