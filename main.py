from services.analyzer import Analyzer

if __name__ == '__main__':
    analyzer = Analyzer()
    analyzer.run()
    print(analyzer.results)
