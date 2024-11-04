import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_ORGANIZATION = os.environ.get('OPENAI_ORGANIZATION')
    OPENAI_PROJECT = os.environ.get('OPENAI_PROJECT')
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    FUNCTION_SMELL_ASSISTANT_ID = 'asst_q3U8t17fN67BBxZYmp68rHWo'
    DB_PATH = './data/code_smell_analysis.db'
    DATASET_PATH = './data/MLCQCodeSmellSamples.csv'
