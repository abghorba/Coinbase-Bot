import os

from dotenv import load_dotenv

# Load environment variables
path_to_dotenv_file = os.getcwd() + "/.env"
load_dotenv(path_to_dotenv_file)


class CoinbaseProCredentials:
    """Coinbase Pro API keys"""

    def __init__(self):
        self.api_key = os.getenv("CB_API_KEY")
        self.secret_key = os.getenv("CB_API_SECRET")
        self.passphrase = os.getenv("CB_API_PASS")

    @property
    def empty_credentials(self):
        """True if any credential is empty; False otherwise"""

        return not (bool(self.api_key) and bool(self.secret_key) and bool(self.passphrase))


class CoinbaseSandboxCredentials:
    """Coinbase Sandbox API keys"""

    def __init__(self):
        self.api_key = os.getenv("CB_API_KEY_TEST")
        self.secret_key = os.getenv("CB_API_SECRET_TEST")
        self.passphrase = os.getenv("CB_API_PASS_TEST")

    @property
    def empty_credentials(self):
        """True if any credential is empty; False otherwise"""

        return not (bool(self.api_key) and bool(self.secret_key) and bool(self.passphrase))


class EmailCredentials:
    """User's email credentials"""

    def __init__(self):
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.password = os.getenv("EMAIL_PASSWORD")

    @property
    def empty_credentials(self):
        """True if any credential is empty; False otherwise"""

        return not (bool(self.email_address) and bool(self.password))
