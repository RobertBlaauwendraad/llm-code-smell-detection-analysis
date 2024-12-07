from config.config import Config
from data.code_sample import CodeSample
from data.code_scope import CodeScope
from data.code_smell import CodeSmell
from services.smell_analyzer.base_smell_analyzer import BaseSmellAnalyzer

BLOB_AMOUNTS = {'none': 15, 'minor': 3, 'major': 1, 'critical': 1}
DATA_CLASS_AMOUNTS = {'none': 14, 'minor': 3, 'major': 2, 'critical': 1}
LONG_METHOD_AMOUNTS = {'none': 15, 'minor': 3, 'major': 1, 'critical': 1}
FEATURE_ENVY_AMOUNTS = {'none': 17, 'minor': 1, 'major': 1, 'critical': 1}

class CombinedSmellAnalyzer(BaseSmellAnalyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, ids):
        smells = CodeSmell.get_smells_by_ids(self.conn, ids)
        scopes = {}

        for smell in smells:
            code_sample = CodeSample.get_by_id(self.conn, smell.code_sample_id)
            code_scope = CodeScope.get_by_id_and_types(self.conn, code_sample.id, ['class', 'extended_function'])
            if code_scope and code_scope.id not in scopes:
                scopes[code_scope.id] = code_scope

        for scope_id, scope in scopes.items():
            openai_response = self.client.get_response(Config.COMBINED_SMELL_ASSISTANT_ID, scope.code_segment)
            self.count_results(openai_response, scope, smells)

    def get_develop_set(self):
        develop_set = []
        for severity, amount in BLOB_AMOUNTS.items():
            develop_set.extend(
                CodeSmell.get_development_ids(self.conn, 'blob', severity, 'class', amount))
        for severity, amount in DATA_CLASS_AMOUNTS.items():
            develop_set.extend(
                CodeSmell.get_development_ids(self.conn, 'data class', severity, 'class', amount))
        for severity, amount in LONG_METHOD_AMOUNTS.items():
            develop_set.extend(
                CodeSmell.get_development_ids(self.conn, 'long method', severity, 'extended_function', amount))
        for severity, amount in FEATURE_ENVY_AMOUNTS.items():
            develop_set.extend(
                CodeSmell.get_development_ids(self.conn, 'feature envy', severity, 'extended_function', amount))
        return develop_set

    def view_results(self):
        print('Combined Smell Results')
        super().view_results()

    def view_scores(self):
        print('Combined Smell Scores')
        super().view_scores()