from datetime import datetime

import requests

from src.coinbase.frequency import FREQUENCY_TO_DAYS


class DataInputVerifier:
    @staticmethod
    def is_valid_date_string(date_string):
        """
        Checks if provided date string is non-null and is in format YYYY-MM-DD.

        :param date_string: str
        :return: True if valid; False otherwise
        """

        if not isinstance(date_string, str):
            print(f"ERROR: date_string cannot be of type {type(date_string)}")
            return False

        # Null check
        if not date_string:
            print("ERROR: date_string cannot be null.")
            return False

        # Make sure the date is in the correct format
        try:
            datetime.strptime(date_string, "%Y-%m-%d")

        except ValueError:
            print(f"ERROR: Inputted date {date_string} is not in format YYYY-MM-DD.")
            return False

        return True

    @staticmethod
    def is_valid_time_string(time_string):
        """
        Checks if provided time string is non-null and is in format HH:MM XM.

        :param time_string: str
        :return: True if valid; False otherwise
        """

        if not isinstance(time_string, str):
            print(f"ERROR: date_string cannot be of type {type(time_string)}")
            return False

        # Null check
        if not time_string:
            print("ERROR: time_string cannot be null.")
            return False

        # Make sure the time is in the correct format
        try:
            datetime.strptime(time_string, "%I:%M %p").time()

        except ValueError:
            print(f"ERROR: Inputted time {time_string} is not in format HH:MM XM.")
            return False

        # HH:MM XM --> [HH:MM, XM] --> split HH:MM --> [HH, MM]
        time_string_minute_component = time_string.split(" ")[0].split(":")[1]
        if len(time_string_minute_component) < 2:
            return False

        return True

    @staticmethod
    def is_valid_date_and_time_to_start(date_string, time_string):
        """
        Given the date_string in YYYY-MM-DD format and the time_string in HH:MM XM format, determine if this is a
        valid start. The datetime is valid if it comes after the current datetime and is not within 60 seconds
        of the current time.

        :param date_string: str
        :param time_string: str
        :return: True if valid; False otherwise
        """

        # Null checks
        if not date_string:
            print("ERROR: date_string cannot be null.")
            return False

        if not time_string:
            print("ERROR: time_string cannot be null.")
            return False

        datetime_string = f"{date_string} {time_string}"

        # Make sure the datetime string is in the correct format
        try:
            datetime_obj = datetime.strptime(datetime_string, "%Y-%m-%d %I:%M %p")

        except ValueError:
            print(f"ERROR: Datetime string {datetime_string} is not in format YYYY-MM-DD HH:MM XM.")
            return False

        if datetime_obj < datetime.now():
            print(f"ERROR: Datetime string {datetime_string} cannot occur before the current date and time.")
            return False

        time_delta = datetime_obj - datetime.now()

        if time_delta.seconds < 60:
            print(f"ERROR: Datetime string {datetime_string} cannot be within 60 seconds of the current time.")
            return False

        return True

    @staticmethod
    def is_valid_frequency(frequency):
        """
        Checks if provided frequency is valid.

        :param frequency: str
        :return: True if valid; False otherwise
        """

        if not isinstance(frequency, str):
            return False

        # Null check
        if not frequency:
            print("Frequency cannot be null.")
            return False

        # Check frequency is valid
        if frequency.lower() not in FREQUENCY_TO_DAYS:
            print(
                f'Invalid value {frequency.lower()}. Valid values include "daily", "weekly", "biweekly", and "monthly".'
            )
            return False

        return True

    @staticmethod
    def is_valid_crypto(crypto):
        """
        Checks if provided crypto string is valid.

        :param crypto: str
        :return: True if valid; False otherwise
        """

        if not isinstance(crypto, str):
            return False

        # Null check
        if not crypto:
            print("Crypto symbol cannot be null.")
            return False

        if not crypto.isalpha():
            return False

        crypto = crypto.upper()

        # Check if the API supports the inputted crypto.
        r = requests.get("https://api.exchange.coinbase.com/currencies/" + crypto)
        if r.status_code != 200:
            print(f"Invalid crypto symbol {crypto}.")
            return False

        return True

    @staticmethod
    def is_valid_dollar_amount(dollar_amount):
        """
        Checks if the dollar amount string is valid.

        :param dollar_amount: str
        :return: True if valid; False otherwise
        """

        if not isinstance(dollar_amount, str):
            return False

        # Null check
        if not dollar_amount:
            print("Dollar amount cannot be null.")
            return False

        # Check for value errors
        try:
            assert float(dollar_amount) > 0

        except ValueError:
            print(f"The dollar amount {dollar_amount} must be a numerical value.")
            return False

        except AssertionError:
            print(f"The dollar amount {dollar_amount} must be greater than 0")
            return False

        return True
