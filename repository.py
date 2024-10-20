import github3


def get_repo_name(full_repo_name):
    return full_repo_name.replace("git@github.com:", "").replace(".git", "")


class Repository:
    def __init__(self, token):
        self.gh = github3.login(token=token)

    def get_file_content(self, repo_name, commit_hash, filename):
        repo_name = get_repo_name(repo_name)
        repo = self.gh.repository(*repo_name.split('/'))
        commit = repo.commit(commit_hash)
        file_content = repo.file_contents(filename, ref=commit.sha)
        return file_content.decoded.decode('utf-8')
