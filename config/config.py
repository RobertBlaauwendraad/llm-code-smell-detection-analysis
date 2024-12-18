import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_ORGANIZATION = os.environ.get('OPENAI_ORGANIZATION')
    OPENAI_PROJECT = os.environ.get('OPENAI_PROJECT')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    ASSISTANT_ID = 'asst_8TPp3H5Gtjh8lVPZDE6T3QUc'
    DB_PATH = './data/code_smell_detection_analysis.db'
    DATASET_PATH = './data/MLCQCodeSmellSamples.csv'
    PROMPT_STRATEGIES = {
        'zero-shot': 'asst_8TPp3H5Gtjh8lVPZDE6T3QUc',
        'few-shot': 'asst_vDqW8qhUVOICnIojIgmqm2p2',
        'chain-of-thought': 'asst_XorQC7WYAv9nasySxftwVRO3',
        'role_prompting': 'asst_dgboDtdnug9J0MOk4IoSuUJ6',
        'combined_prompt': 'asst_4LqtQpbTLilEENlisf4kbEcy'
    }