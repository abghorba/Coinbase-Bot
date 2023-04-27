#!/bin/sh

if [ ! -d "env" ]; then
    echo "Creating virtual environment: env"
    python3 -m venv env
    source env/bin/activate
    echo "Upgrading pip..."
    python3 -m pip install --upgrade pip
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo "Installing pre-commit hooks..."
    pre-commit install
    echo "Done!"
fi


# Coinbase API keys
CB_API_KEY=""
CB_API_SECRET=""
CB_API_PASS=""

# Coinbase Sandbox API keys
CB_API_KEY_TEST=""
CB_API_SECRET_TEST=""
CB_API_PASS_TEST=""

# User's email credentials
EMAIL_ADDRESS=""
EMAIL_PASSWORD=""

if [ ! -f ".env" ]; then
    echo "Creating .env file to store environment variables..."
    touch .env
    echo "CB_API_KEY = \"$CB_API_KEY\"" >> .env
    echo "CB_API_SECRET = \"$CB_API_SECRET\"" >> .env
    echo "CB_API_PASS = \"$CB_API_PASS\"" >> .env
    echo "CB_API_KEY_TEST = \"$CB_API_KEY_TEST\"" >> .env
    echo "CB_API_SECRET_TEST = \"$CB_API_SECRET_TEST\"" >> .env
    echo "CB_API_PASS_TEST = \"$CB_API_PASS_TEST\"" >> .env
    echo "EMAIL_ADDRESS = \"$EMAIL_ADDRESS\"" >> .env
    echo "EMAIL_PASSWORD = \"$EMAIL_PASSWORD\"" >> .env
    echo "Done!"
fi