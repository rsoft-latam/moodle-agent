import os
from dotenv import load_dotenv

ENV = os.getenv('ENV', 'local')

if ENV != 'prod':
    load_dotenv()
    print('Variables loaded from .env file')
else:
    print ('Variables loaded from AWS')

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
OPENAI_MODEL = os.environ['OPENAI_MODEL']

MOODLE_BASE_URL = os.environ['MOODLE_BASE_URL']
MOODLE_SERVICE = os.environ['MOODLE_SERVICE']
MOODLE_USERNAME = os.environ['MOODLE_USERNAME']
MOODLE_PASSWORD = os.environ['MOODLE_PASSWORD']

WHATSAPP_TOKEN = os.environ['WHATSAPP_TOKEN']
WHATSAPP_VERIFY_TOKEN = os.environ['WHATSAPP_VERIFY_TOKEN']
WHATSAPP_PHONE_ID = os.environ['WHATSAPP_PHONE_ID']