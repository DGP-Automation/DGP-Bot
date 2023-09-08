import os
from dotenv import load_dotenv

load_dotenv()

# Private Key
PRIVATE_KEY_PATH = os.getenv('PRIVATE_KEY_PATH')
PRIVATE_KEY = open(PRIVATE_KEY_PATH, "r").read()
# App ID
APP_ID = os.getenv('APP_ID')
# Installation ID
INSTALLATION_ID = os.getenv('INSTALLATION_ID')
# GitHub Personal Token
GITHUB_PERSONAL_TOKEN = os.getenv('GITHUB_PERSONAL_TOKEN')

# Global Variables
access_token = ""
access_token_generated_time = 0
