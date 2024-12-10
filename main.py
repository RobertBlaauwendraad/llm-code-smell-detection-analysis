from services.analyzer import Analyzer

if __name__ == '__main__':
    analyzer = Analyzer()
    analyzer.run()
    analyzer.view_heatmaps()
    analyzer.binary_evaluation()
    analyzer.ordinal_evaluation()
