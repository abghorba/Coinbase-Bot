from datetime import datetime

import requests

from src.coinbase.frequency import FREQUENCY_TO_DAYS

BASE_URL = "https://api.exchange.coinbase.com/currencies/"


class InputCollector:
    def __init__(self):
        self.start_date_is_today = False

        # collect_inputs()
        self.start_date = None
        self.start_time = None
        self.frequency = None
        self.orders = None

    def is_valid_start_date(self, date_string):
        """
        Checks if provided date string is valid.

        :param date_string: str
        :return: True if valid; False otherwise
        """

        if not isinstance(date_string, str):
            return False

        # Null check
        if not date_string:
            print("Date cannot be null.")
            return False

        # Make sure it's a valid date
        try:
            date_format = "%Y-%m-%d"
            converted_date = datetime.strptime(date_string, date_format)

        except ValueError:
            print("This date does not exist!")
            return False

        # Make sure the date isn't before the current day
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if converted_date < current_date:
            print("The date must occur on or after the current date.")
            return False

        # Need to know if today is the start date for time validation
        if converted_date == current_date:
            self.start_date_is_today = True

        return True

    def get_start_date(self):
        """
        Checks if the start date the user inputs is valid.

        :return: The date string in format YYYY-MM-DD
        """

        valid_date = False

        while not valid_date:
            date = input("Enter in the start date in format YYYY-MM-DD: ")
            valid_date = self.is_valid_start_date(date)

        return date

    def is_valid_start_time(self, time_string):
        """
        Checks if provided time string is valid.

        :param time_string: str
        :return: True if valid; False otherwise
        """

        if not isinstance(time_string, str):
            return False

        # Null check
        if not time_string:
            print("Time cannot be null.")
            return False

        # Make sure its a valid time
        try:
            format = "%I:%M %p"
            converted_time = datetime.strptime(time_string, format).time()

        except ValueError:
            print("This is not a valid time.")
            return False

        # If the start date is today, the time must occur after the current time.
        if self.start_date_is_today:
            current_time = datetime.now().time()

            if converted_time < current_time:
                print("The chosen start date is today. The time of the transaction must occur after the current time.")
                return False

        return True

    def get_start_time(self):
        """
        Checks if the start time the user inputs is valid.

        :return: The time in format HH:MM XM
        """

        valid_start_time = False

        while not valid_start_time:
            start_time = input("Enter in the time you wish to conduct transactions in format HH:MM XM: ")

            valid_start_time = self.is_valid_start_time(start_time)

        return start_time

    def is_valid_frequency(self, frequency):
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
            print('Invalid value. Valid values include "daily", "weekly", "biweekly", and "monthly".')
            return False

        return True

    def get_frequency(self):
        """
        Checks if the frequency the user inputs is valid.

        :return: The frequency of the transactions as a string
        """

        valid_frequency = False

        while not valid_frequency:
            frequency = input(
                'How often would you like to make purchases? Valid values include "daily", "weekly", '
                '"biweekly", and "monthly": '
            )

            valid_frequency = self.is_valid_frequency(frequency)

        return frequency

    def is_valid_crypto(self, crypto):
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
        r = requests.get(BASE_URL + crypto)
        if r.status_code != 200:
            print("Invalid crypto symbol.")
            return False

        return True

    def is_valid_dollar_amount(self, dollar_amount):
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
            print("The dollar amount must be a numerical value.")
            return False

        except AssertionError:
            print("The dollar amount must be greater than 0")
            return False

        return True

    def get_orders(self):
        """
        Constructs a dictionary of each order.

        :return: Dict with key-value pair "crypto" : dollar_amount
        """

        keep_ordering = True
        orders = {}

        while keep_ordering:
            # Grab the crypto symbol first
            valid_crypto = False

            while not valid_crypto:
                crypto = input("Enter in the cryprocurrency symbol you wish to purchase: ")

                valid_crypto = self.is_valid_crypto(crypto)

            # There is already a pending order for the inputted cryptocurrency
            if crypto in orders:
                overwrite_order = input(
                    "There is already a pending order for this cryptocurrency. Continuing will "
                    "overwrite the previous order. Continue? Y/N "
                )

                if overwrite_order == "N" or overwrite_order == "n":
                    continue

            # Next grab the dollar amount
            valid_dollar_amount = False

            while not valid_dollar_amount:
                dollar_amount = input("Enter in the amount in USD to purchase with: ")

                valid_dollar_amount = self.is_valid_dollar_amount(dollar_amount)

            # Add order into dictionary
            orders[crypto] = float(dollar_amount)

            # Continue adding orders if requested
            wish_to_continue = input("Do you wish to add more orders? Y/N ")

            if wish_to_continue == "N" or wish_to_continue == "n":
                keep_ordering = False

        return orders

    def collect_inputs(self):
        """Driver function to collect all inputs from user."""

        self.start_date = self.get_start_date()
        self.start_time = self.get_start_time()
        self.frequency = self.get_frequency()
        self.orders = self.get_orders()
