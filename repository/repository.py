import github3
from github3.exceptions import UnprocessableEntity, NotFoundError

from config.config import Config


class Repository:
    def __init__(self):
        self.gh = github3.login(Config.GITHUB_TOKEN)

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

    def get_rate_limit(self):
        return self.gh.rate_limit()
