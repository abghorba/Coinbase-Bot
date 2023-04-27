import os

from dotenv import load_dotenv

# Load environment variables
path_to_dotenv_file = os.getcwd() + "/.env"
load_dotenv(path_to_dotenv_file)

# Coinbase API keys
CB_API_KEY = os.getenv("CB_API_KEY")
CB_API_SECRET = os.getenv("CB_API_SECRET")
CB_API_PASS = os.getenv("CB_API_PASS")

# Coinbase Sandbox API keys
CB_API_KEY_TEST = os.getenv("CB_API_KEY_TEST")
CB_API_SECRET_TEST = os.getenv("CB_API_SECRET_TEST")
CB_API_PASS_TEST = os.getenv("CB_API_PASS_TEST")

# User's email credentials
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
