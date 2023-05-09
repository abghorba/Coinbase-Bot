from src.orders.input_collection import InputCollector
from src.orders.utilities import DataInputVerifier


class CommandLineInputCollector(InputCollector):
    def get_start_date(self):
        """
        Checks if the start date the user inputs is valid.

        :return: The date string in format YYYY-MM-DD
        """

        valid_date = False
        start_date = None

        while not valid_date:
            start_date = input("Enter in the start date in format YYYY-MM-DD: ")
            valid_date = DataInputVerifier.is_valid_date_string(start_date)

        return start_date

    def get_start_time(self):
        """
        Checks if the start time the user inputs is valid.

        :return: The time in format HH:MM XM
        """

        valid_time = False
        start_time = None

        while not valid_time:
            start_time = input("Enter in the time you wish to conduct transactions in format HH:MM XM: ")
            valid_time = DataInputVerifier.is_valid_time_string(start_time)

        return start_time

    def get_start_datetime(self):
        """
        Checks if the start time the user inputs is valid.

        :return: tuple of (Start date in format YYYY-MM-DD, Start time in format HH:MM XM)
        """

        valid_datetime = False
        start_date = None
        start_time = None

        while not valid_datetime:
            start_date = self.get_start_date()
            start_time = self.get_start_time()
            valid_datetime = DataInputVerifier.is_valid_date_and_time_to_start(start_date, start_time)

        return start_date, start_time

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

            valid_frequency = DataInputVerifier.is_valid_frequency(frequency)

        return frequency

    def get_orders(self):
        """
        Constructs a dictionary of each order.

        :return: Dict with key-value pair "crypto" : dollar_amount
        """

        keep_ordering = True
        orders = {}

        while keep_ordering:
            # Grab the crypto symbol first
            crypto = None
            valid_crypto = False

            while not valid_crypto:
                crypto = input("Enter in the cryptocurrency symbol you wish to purchase: ")
                valid_crypto = DataInputVerifier.is_valid_crypto(crypto)

            # There is already a pending order for the inputted cryptocurrency
            if crypto in orders:
                overwrite_order = input(
                    "There is already a pending order for this cryptocurrency. Continuing will "
                    "overwrite the previous order. Continue? Y/N "
                )

                if overwrite_order == "N" or overwrite_order == "n":
                    wish_to_continue = input("Do you wish to add more orders? Y/N ")

                    if wish_to_continue == "N" or wish_to_continue == "n":
                        keep_ordering = False

                    continue

            # Next grab the dollar amount
            dollar_amount = None
            valid_dollar_amount = False

            while not valid_dollar_amount:
                dollar_amount = input("Enter in the amount in USD to purchase with: ")
                valid_dollar_amount = DataInputVerifier.is_valid_dollar_amount(dollar_amount)

            # Add order into dictionary
            orders[crypto] = float(dollar_amount)

            # Continue adding orders if requested
            wish_to_continue = input("Do you wish to add more orders? Y/N ")

            if wish_to_continue == "N" or wish_to_continue == "n":
                keep_ordering = False

        return orders

    def collect_inputs(self):
        """Driver function to collect all inputs from user."""

        self.start_date, self.start_time = self.get_start_datetime()
        self.frequency = self.get_frequency()
        self.orders = self.get_orders()
