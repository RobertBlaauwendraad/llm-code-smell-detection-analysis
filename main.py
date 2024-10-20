import csv
import json
from pyexpat.errors import messages

import github3
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_data_list(path):
    with open(path, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        data_list = []
        for row in reader:
            data_list.append(row)
    return data_list

def get_repo_name(full_repo_name):
    return full_repo_name.replace("git@github.com:", "").replace(".git", "")

def get_file_content(repo_name, commit_hash, filename, token):
    gh = github3.login(token=token)
    repo = gh.repository(*repo_name.split('/'))
    commit = repo.commit(commit_hash)
    file_content = repo.file_contents(filename, ref=commit.sha)
    return file_content.decoded.decode('utf-8')

def get_snippet(file_content, start_line, end_line):
    lines = file_content.split("\n")
    snippet = "\n".join(lines[start_line-1:end_line])
    return snippet

def get_code_smells(data_list, github_token, limit=None):
    code_smells = []
    for i, data in enumerate(data_list):
        if limit is not None and i >= limit:
            break
        repository = data["repository"]
        commit_hash = data["commit_hash"]
        path = data["path"]
        start_line = int(data["start_line"])
        end_line = int(data["end_line"])
        file_content = get_file_content(get_repo_name(repository), commit_hash, path, github_token)
        snippet = get_snippet(file_content, start_line, end_line)
        code_smell = {
            id: data["id"],
            "smell": data["smell"],
            "severity": data["severity"],
            "type": data["type"],
            "snippet": snippet
        }
        code_smells.append(code_smell)
    return code_smells

if __name__ == '__main__':
    path = "data/MLCQCodeSmellSamples.csv"
    github_token = os.environ.get('GITHUB_TOKEN')
    data_list = get_data_list(path)
    code_smells = get_code_smells(data_list, github_token, limit=10)

    client = OpenAI(
        api_key=os.environ.get('OPENAI_API_KEY'),
        organization=os.environ.get('OPENAI_ORGANIZATION'),
        project=os.environ.get('OPENAI_PROJECT'),
    )
    assistant = client.beta.assistants.retrieve("asst_q3U8t17fN67BBxZYmp68rHWo")

    code_smells_responses = []
    for code_smell in code_smells:
        run = client.beta.threads.create_and_run(
            assistant_id="asst_q3U8t17fN67BBxZYmp68rHWo",
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": code_smell["snippet"]
                    }
                ]
            },
        )

        while run.status != "completed":
            run = client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)

        messages = client.beta.threads.messages.list(thread_id=run.thread_id)
        response = messages.data[0].content[0].text.value
        json_response = json.loads(response)

        del code_smell["snippet"]
        code_smells_responses.append({
            "code_smell": code_smell,
            "response": json_response
        })

    print(code_smells_responses)