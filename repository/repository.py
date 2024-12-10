import base64
import re

import github3
import requests
from requests import HTTPError

from config.config import Config


class Repository:
    def __init__(self):
        self.gh = github3.login(token=Config.GITHUB_TOKEN)

    def get_file_content(self, repository, commit_hash, path):
        try:
            # Construct the API URL
            repo_owner, repo_name = repository.replace("git@github.com:", "").replace(".git", "").split('/')
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}"
            headers = {"Authorization": f"token {Config.GITHUB_TOKEN}"}
            params = {"ref": commit_hash}

            # Make the single API call
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the response and decode the content
            file_content = response.json()
            content_base64 = file_content.get('content', None)
            if content_base64 is None:
                return None

            # Decode the base64 content into bytes and then into a UTF-8 string
            return base64.b64decode(content_base64).decode('utf-8')
        except HTTPError:
            return None

    def get_segment(self, repository, commit_hash, path, start_line, end_line):
        file_content = self.get_file_content(repository, commit_hash, path)
        if file_content is None:
            return None
        lines = file_content.split("\n")
        return "\n".join(lines[start_line - 1:end_line])

    def get_extended_segment(self, repository, commit_hash, path, start_line):
        file_content = self.get_file_content(repository, commit_hash, path)
        if file_content is None or file_content == '':
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
        class_pattern = re.compile(
            r"^\s*(?:@\w+\s+)*\s*(public|protected|private)?\s*(static)?\s*(abstract|final)?\s*class\s+(\w+)(?:<[^>]+>)?\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w, ]+)?\s*")
        for i in range(start_line - 1, -1, -1):
            if class_pattern.match(lines[i]):
                class_start_line = i + 1
                break

        if class_start_line is None:
            return None

        # Find the end of the class using curly brackets
        class_end_line = len(lines)
        open_braces = 0
        for i in range(class_start_line - 1, len(lines)):
            open_braces += lines[i].count("{")
            open_braces -= lines[i].count("}")
            if open_braces == 0:
                class_end_line = i + 1
                break

        return "\n".join(lines[class_start_line - 1:class_end_line])

    def get_rate_limit(self):
        return self.gh.rate_limit()
