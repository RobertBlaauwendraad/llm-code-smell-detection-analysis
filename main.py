import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from repository import Repository
from code_smell_analyzer import CodeSmellAnalyzer, get_data_list

class Main:
    def __init__(self):
        load_dotenv()
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.openai_organization = os.environ.get('OPENAI_ORGANIZATION')
        self.openai_project = os.environ.get('OPENAI_PROJECT')
        self.repository = Repository(self.github_token)
        self.analyzer = CodeSmellAnalyzer(self.repository)
        self.client = OpenAI(
            api_key=self.openai_api_key,
            organization=self.openai_organization,
            project=self.openai_project,
        )

    def analyze_code_smells(self, path, limit=None):
        data_list = get_data_list(path)
        return self.analyzer.get_code_smells(data_list, limit=limit)

    def get_openai_response(self, snippet):
        run = self.client.beta.threads.create_and_run(
            assistant_id="asst_q3U8t17fN67BBxZYmp68rHWo",
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": snippet
                    }
                ]
            },
        )

        while run.status != "completed":
            run = self.client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)

        messages = self.client.beta.threads.messages.list(thread_id=run.thread_id)
        response = messages.data[0].content[0].text.value
        return json.loads(response)

    def run(self, path, limit=None):
        code_smells = self.analyze_code_smells(path, limit=limit)
        code_smells_responses = []

        for code_smell in code_smells:
            response = self.get_openai_response(code_smell["snippet"])
            del code_smell["snippet"]
            code_smells_responses.append({
                "code_smell": code_smell,
                "response": response
            })

        return code_smells_responses

if __name__ == '__main__':
    main = Main()
    code_smells_responses = main.run("data/MLCQCodeSmellSamples.csv", limit=1)
    print(code_smells_responses)