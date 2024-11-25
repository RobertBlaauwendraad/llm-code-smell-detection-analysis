import re

import github3
from github3.exceptions import UnprocessableEntity, NotFoundError

from config.config import Config


class Repository:
    def __init__(self):
        self.gh = github3.login(token=Config.GITHUB_TOKEN)

    def get_file_content(self, repository, commit_hash, path):
        try:
            repository = repository.replace("git@github.com:", "").replace(".git", "")
            repo = self.gh.repository(*repository.split('/'))
            commit = repo.commit(commit_hash)
            file_content = repo.file_contents(path, ref=commit.sha)
            return file_content.decoded.decode('utf-8')
        except (UnprocessableEntity, NotFoundError, AttributeError):
            return None

    def get_segment(self, repository, commit_hash, path, start_line, end_line):
        file_content = self.get_file_content(repository, commit_hash, path)
        if file_content is None:
            return None
        lines = file_content.split("\n")
        return "\n".join(lines[start_line - 1:end_line])

    def get_extended_segment(self, repository, commit_hash, path, start_line, end_line):
        file_content = self.get_file_content(repository, commit_hash, path)
        if file_content is None:
            return None
        lines = file_content.split("\n")

        # Find the start of the class
        class_start_line = None
        # Optional annotations (e.g., @Entity)
        # Optional access modifiers (e.g., public, protected, private)
        # Optional static, abstract, or final keywords
        # Class name with optional generics (e.g., class MyClass<T>)
        # Optional extends clause
        # Optional implements clause
        class_pattern = re.compile(r"^\s*(?:@\w+\s+)*\s*(public|protected|private)?\s*(static)?\s*(abstract|final)?\s*class\s+(\w+)(?:<[^>]+>)?\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w, ]+)?\s*")
        for i in range(start_line - 1, -1, -1):
            if class_pattern.match(lines[i]):
                class_start_line = i + 1
                break

        if class_start_line  is None:
            return None

        # Find the end of the class
        class_end_line = len(lines)
        indent_level = len(lines[class_start_line - 1]) - len(lines[class_start_line - 1].lstrip())
        for i in range(start_line, len(lines)):
            if len(lines[i].strip()) > 0 and len(lines[i]) - len(lines[i].lstrip()) <= indent_level:
                class_end_line = i
                break

        return "\n".join(lines[class_start_line - 1:class_end_line])


    def get_rate_limit(self):
        return self.gh.rate_limit()
