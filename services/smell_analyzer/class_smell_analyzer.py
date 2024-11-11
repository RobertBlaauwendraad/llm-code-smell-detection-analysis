from config.config import Config
from data.code_sample import CodeSample
from data.code_scope import CodeScope
from data.code_smell import CodeSmell
from services.smell_analyzer.base_smell_analyzer import BaseSmellAnalyzer


class ClassSmellAnalyzer(BaseSmellAnalyzer):
    def __init__(self):
        super().__init__()

    def analyze(self, ids):
        smells = CodeSmell.get_smells_by_ids(self.conn, ids)
        scopes = {}

        for smell in smells:
            code_sample = CodeSample.get_by_id(self.conn, smell.code_sample_id)
            code_scope = CodeScope.get_by_id_and_type(self.conn, code_sample.id, 'class')
            if code_scope and code_scope.id not in scopes:
                scopes[code_scope.id] = code_scope

        for scope_id, scope in scopes.items():
            openai_response = self.client.get_response(Config.CLASS_SMELL_ASSISTANT_ID, scope.code_segment)
            self.count_results(openai_response, scope, smells)

    def view_results(self):
        print('Class Smell Results')
        super().view_results()

    def view_scores(self):
        print('Class Smell Scores')
        super().view_scores()