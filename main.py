from services.analyzer import Analyzer

if __name__ == '__main__':
    analyzer = Analyzer()
    analyzer.run(use_cached=True)
    analyzer.view_heatmaps()
    analyzer.binary_evaluation()
    analyzer.ordinal_evaluation()
