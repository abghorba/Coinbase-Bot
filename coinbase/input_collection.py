import requests

from coinbase.frequency import FREQUENCY_TO_DAYS
from datetime import datetime


class InputCollector():

    def __init__(self):
        self.start_date_is_today = False

    def get_start_date(self):
        """
        Checks if the start date the user inputs is valid.
        
        :return: The date string in format YYYY-MM-DD
        """

        valid_date = False

        while not valid_date:

            date = input("Enter in the start date in format YYYY-MM-DD: ")

            # Null check
            if not date:
                print("Date cannot be null.")
                continue

            # Make sure it's a valid date
            try:
                format = "%Y-%m-%d"
                converted_date = datetime.strptime(date, format)

            except ValueError:
                print("This date does not exist!")
                continue

            # Make sure the date isn't before the current day
            current_date = datetime.now().replace(hour=0, minute=0, 
                                                  second=0, microsecond=0)

            if converted_date < current_date:
                print("The date must occur on or after the current date.")
                continue

            # Need to know if today is the start date for time validation
            if converted_date == current_date:
                self.start_date_is_today = True

            valid_date = True

        return date

    def get_start_time(self):
        """
        Checks if the start time the user inputs is valid.

        :return: The time in format HH:MM XM
        """

        valid_start_time = False

        while not valid_start_time:

            start_time = input(
                "Enter in the time you wish to conduct transactions in format HH:MM XM: "
            )

            # Null check
            if not start_time:
                raise TypeError("Time cannot be null.")
                continue

            # Make sure its a valid time
            try:
                format = "%I:%M %p"
                converted_time = datetime.strptime(start_time, format).time()

            except ValueError:
                print("This is not a valid time.")
                continue

            # If the start date is today, the time must occur after the current time.
            if self.start_date_is_today:

                current_time = datetime.now().time()

                if converted_time < current_time:
                    print(
                        "The chosen start date is today. The time of the transaction must occur after the current time."
                    )
                    continue

            valid_start_time = True

        return start_time

    def get_frequency(self):
        """
        Checks if the frequency the user inputs is valid.

        :return: The frequency of the transactions as a string
        """

        valid_frequency = False

        while not valid_frequency:

            frequency = input(
                'How often would you like to make purchases? Valid values include "daily", "weekly", "biweekly", and "monthly": '
            )

            # Null check
            if not frequency:
                print("Frequency cannot be null.")
                continue

            # Check frequency is valid
            if frequency.lower() in FREQUENCY_TO_DAYS:
                valid_frequency = True

            else:
                print(
                    'Invalid value. Valid values include "daily", "weekly", "biweekly", and "monthly".'
                )

        return frequency

    def get_orders(self):
        """
        Constructs a dictionary of each order.

        :return: Dict with key-value pair "crypto" : dollar_amount
        """

        valid_orders = False
        base_url = "https://api.exchange.coinbase.com/currencies/"
        orders = {}

        while not valid_orders:

            # Grab the crypto symbol first
            valid_crypto = False

            while not valid_crypto:
                crypto = input(
                    "Enter in the cryprocurrency symbol you wish to purchase: "
                )
                crypto = crypto.upper()

                # There is already a pending order for the inputted cryptocurrency
                if crypto in orders:
                    overwrite_order = input(
                        "There is already a pending order for this cryptocurrency. Continuing will overwrite the previous order. Continue? Y/N "
                    )

                    if overwrite_order == "N":
                        continue

                # Null check
                if not crypto:
                    print("Crypto symbol cannot be null.")
                    continue

                # Check if the API supports the inputted crypto.
                r = requests.get(base_url + crypto)
                if r.status_code != 200:
                    print("Invalid crypto symbol.")
                    continue

                valid_crypto = True

            # Next grab the dollar amount
            valid_dollar_amount = False

            while not valid_dollar_amount:
                dollar_amount = input("Enter in the amount in USD to purchase with: ")

                # Null check
                if not dollar_amount:
                    print("Dollar amount cannot be null.")
                    continue

                # Check for value errors
                try:
                    orders[crypto] = float(dollar_amount)

                except ValueError:
                    print("The dollar amount must be a numerical value.")
                    continue

                valid_dollar_amount = True

            wish_to_continue = input("Do you wish to add more orders? Y/N ")

            if wish_to_continue == "N":
                valid_orders = True

        return orders

    def collect_inputs(self):
        """Driver function to collect all inputs from user."""

        self.start_date = self.get_start_date()
        self.start_time = self.get_start_time()
        self.frequency = self.get_frequency()
        self.orders = self.get_orders()

