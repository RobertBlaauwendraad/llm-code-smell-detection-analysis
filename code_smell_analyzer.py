import csv

def get_data_list(path):
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        data_list = [row for row in reader]
    return data_list


def get_snippet(file_content, start_line, end_line):
    lines = file_content.split("\n")
    snippet = "\n".join(lines[start_line-1:end_line])
    return snippet


class CodeSmellAnalyzer:
    def __init__(self, repository):
        self.repository = repository

    def get_code_smells(self, data_list, limit=None):
        code_smells = []
        for i, data in enumerate(data_list):
            if limit is not None and i >= limit:
                break
            repository = data["repository"]
            commit_hash = data["commit_hash"]
            path = data["path"]
            start_line = int(data["start_line"])
            end_line = int(data["end_line"])
            file_content = self.repository.get_file_content(repository, commit_hash, path)
            snippet = get_snippet(file_content, start_line, end_line)
            code_smell = {
                "id": data["id"],
                "smell": data["smell"],
                "severity": data["severity"],
                "type": data["type"],
                "snippet": snippet
            }
            code_smells.append(code_smell)
        return code_smells