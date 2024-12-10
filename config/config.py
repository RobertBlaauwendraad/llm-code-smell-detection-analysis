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
    RESULTS_FILE = './data/results.json'
