import github3

class Repository:
    def __init__(self, token):
        self.gh = github3.login(token=token)

    def get_file_content(self, repo_name, commit_hash, filename):
        repo_name = repo_name.replace("git@github.com:", "").replace(".git", "")
        repo = self.gh.repository(*repo_name.split('/'))
        commit = repo.commit(commit_hash)
        file_content = repo.file_contents(filename, ref=commit.sha)
        return file_content.decoded.decode('utf-8')