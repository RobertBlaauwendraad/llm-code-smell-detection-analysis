import json

from openai import OpenAI

from config.config import Config


class OpenAIClient:
    def __init__(self, assistant_id):
        self.client = OpenAI(
            api_key=Config.OPENAI_API_KEY,
            organization=Config.OPENAI_ORGANIZATION,
            project=Config.OPENAI_PROJECT,
        )
        self.assistant_id = assistant_id

    def get_response(self, code_segment):
        run = self.client.beta.threads.create_and_run(
            assistant_id=self.assistant_id,
            thread={
                "messages": [
                    {
                        "role": "user",
                        "content": code_segment
                    }
                ]
            },
        )

        while run.status != "completed":
            run = self.client.beta.threads.runs.retrieve(thread_id=run.thread_id, run_id=run.id)

        messages = self.client.beta.threads.messages.list(thread_id=run.thread_id)
        response = messages.data[0].content[0].text.value
        return json.loads(response)
