import os
from dotenv import load_dotenv
from repository import Repository

class Main:
    def __init__(self):
        load_dotenv()
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.openai_organization = os.environ.get('OPENAI_ORGANIZATION')
        self.openai_project = os.environ.get('OPENAI_PROJECT')
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.repository = Repository(self.github_token)


if __name__ == '__main__':
    main = Main()