import base64
import hashlib
import hmac
import json
import requests
import smtplib
import time

from config import EMAIL_ADDRESS
from config import EMAIL_PASSWORD
from coinbase.frequency import FREQUENCY_TO_DAYS
from datetime import datetime
from datetime import timedelta
from email.message import EmailMessage
from requests.auth import AuthBase


COINBASE_API_URL = "https://api.pro.coinbase.com/"


# Create custom authentication for Exchange.
class CoinbaseExchangeAuth(AuthBase):

    def __init__(self, api_key, secret_key, passphrase):
        
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or "")
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode()

        request.headers.update(
            {
                "CB-ACCESS-SIGN": signature_b64,
                "CB-ACCESS-TIMESTAMP": timestamp,
                "CB-ACCESS-KEY": self.api_key,
                "CB-ACCESS-PASSPHRASE": self.passphrase,
                "Content-Type": "application/json",
            }
        )

        return request


# Create custom handler for placing orders
class CoinbaseProHandler():

    def __init__(self, api_url, auth):
        self.api_url = api_url
        self.auth = auth

    def get_payment_method(self):
        """
        Retrieves the user's bank from Coinbase Pro
        profile.

        :return: The user's bank ID as a string
        """
        
        payment_id = ""

        response = requests.get(self.api_url + "payment-methods", auth=self.auth)

        if response:
            print("Successfully retrieved payment method.")
            payment_id = response.json()[0]["id"]

        else:
            print("Could not find payment method.")
            print(response.content)

        return payment_id

    def deposit_from_bank(self, amount):
        """
        Deposits USD from user's bank account
        into their USD Wallet on Coinbase Pro.

        :param amount: The amount of USD to deposit
        :return: True if the deposit is successful; False otherwise
        """

        success = False

        if not isinstance(amount, float):
            print("amount must be a number")
            return success

        if amount <= 0:
            print("amount must be a positive number")
            return success

        deposit_request = {
            "amount": amount,
            "currency": "USD",
            "payment_method_id": self.get_payment_method(),
        }

        response = requests.post(
            self.api_url + "deposits/payment-method",
            data=json.dumps(deposit_request),
            auth=self.auth,
        )

        if response:
            print(f"Successfully deposited ${amount:.2f} to Coinbase Pro account.")
            success = True

        else:
            print("Could not make deposit to Coinbase Pro account.")
            print(response.content)

        return success

    def place_market_order(self, product, amount):
        """
        Places a market order for specified
        product with a specified amount of USD.

        :param product: The cryptocurrency to purchase as a string
        :param amount: The amount of USD to make a purchase with
        :return: True if the market order is successfully executed; False otherwise
        """

        success = False

        if not product:
            print("Please specify product.")
            return success

        elif not amount:
            print("Please specify amount.")
            return success

        market_order = {
            "type": "market",
            "side": "buy",
            "product_id": product + "-USD",
            "funds": amount,
        }

        response = requests.post(
            self.api_url + "orders", data=json.dumps(market_order), auth=self.auth
        )

        if response:
            print(f"Successfully made a market order for ${amount} of {product}.")
            success = True

            # Sleep for 15 seconds to ensure Coinbase API updates
            time.sleep(15)

        else:
            print("Could not place market order.")
            print(response.content)

        return success

    def get_transaction_details(self, product, start_date):
        """
        Retrieves the JSON response of the transaction details.

        :param product: The cyptocurrency to get transaction details of as a string
        :param start_date: String in "yyyy-mm-dd" format
        :return: Extracted details from the retrieved JSON as a dict
        """

        fill_parameters = {"product_id": product + "-USD", "start_date": start_date}

        response = requests.get(
            self.api_url + "fills", params=fill_parameters, auth=self.auth
        )

        if response.status_code != 200:
            print("Could not find transaction details")
            return {}

        # Parse the JSON response
        transaction = response.json()[0]

        coinbase_fee = round(float(transaction["fee"]), 2)
        amount_invested = round(float(transaction["usd_volume"]), 2)
        purchase_price = round(float(transaction["price"]), 2)
        purchase_amount = transaction["size"]

        parsed_transaction = {
            "product": product,
            "start_date": start_date,
            "coinbase_fee": "%.2f" % coinbase_fee,
            "amount_invested": "%.2f" % amount_invested,
            "purchase_price": "%.2f" % purchase_price,
            "purchase_amount": purchase_amount,
            "total_amount": "%.2f" % (coinbase_fee + amount_invested),
        }

        return parsed_transaction

    def send_email_confirmation(self, transaction_details):
        """
        Send's user a confirmation email with
        the details of the transaction.

        :param transaction_details: Dict containing transaction details
        :return: True if the email is sent successfully; False otherwise
        """

        success = False

        if not transaction_details:
            print("Transaction details cannot be null")
            return success

        product = transaction_details["product"]
        start_date = transaction_details["start_date"]
        coinbase_fee = transaction_details["coinbase_fee"]
        amount_invested = transaction_details["amount_invested"]
        purchase_price = transaction_details["purchase_price"]
        purchase_amount = transaction_details["purchase_amount"]
        total_amount = transaction_details["total_amount"]

        msg = EmailMessage()
        msg["Subject"] = f"Your Purchase of ${total_amount} of {product} Was Successful!"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = EMAIL_ADDRESS

        content = f"Hello,\n\n You successfully placed your order! Please see below details:\n\n \
            Amount Purchased: {purchase_amount} {product}\n \
            Purchase Price: ${purchase_price}\n \
            Total Amount: ${total_amount}\n \
            Amount Invested: ${amount_invested}\n \
            Coinbase Fees: ${coinbase_fee}\n \
            Date: {start_date}"

        msg.set_content(content)

        try:

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
                success = True

        except smtplib.SMTPAuthenticationError:
            print("Email credentials are not valid!")
            pass

        return success


class CoinbaseBot():

    def __init__(self, api_url, auth, frequency, start_date, start_time, orders={}):
        self.coinbase = CoinbaseProHandler(api_url, auth)
        self.time_delta = FREQUENCY_TO_DAYS[frequency]
        self.next_purchase_date = self.parse_to_datetime(start_date, start_time)
        self.next_deposit_date = self.next_purchase_date + timedelta(minutes=-1)
        self.orders = orders

    def parse_to_datetime(self, date, time):
        """
        Parses both a date string and a time string into one datetime
        object.

        :param date: The date string in format YYYY-MM-DD
        :param time: The time string in format HH:MM XM
        :return: datetime object representing the passed in date and time strings
        """
        if not date or not time:
            raise ValueError("date and time parameters cannot be null")

        date_and_time = date + " " + time
        format = "%Y-%m-%d %I:%M %p"
        date_and_time = datetime.strptime(date_and_time, format)
        return date_and_time

    def update_frequency(self, new_frequency):
        """
        Updates the frequency of the purchases.

        :param new_frequency: Valid values are "daily", "weekly", "biweekly", "monthly"
        :return: None
        """

        if new_frequency not in FREQUENCY_TO_DAYS:
            raise ValueError("ERROR: Invalid value for new_frequency.")

        self.time_delta = FREQUENCY_TO_DAYS[new_frequency]

    def update_deposit_date(self):
        """Updates to the next deposit date."""

        self.next_deposit_date += self.time_delta

    def update_purchase_date(self):
        """Updates to the next purchase date."""

        self.next_purchase_date += self.time_delta

    def is_time_to_deposit(self):
        """Returns True if the current datetime is the deposit datetime."""

        now = datetime.today().replace(second=0, microsecond=0)

        return now == self.next_deposit_date

    def is_time_to_purchase(self):
        """Returns True if current datetime is the purchase datetime."""

        now = datetime.today().replace(second=0, microsecond=0)

        return now == self.next_purchase_date

    def set_orders(self, **kwargs):
        """
        Sets the orders for recurring purchases.

        :param **kwargs: Any number of key-value pairs for product to amount.
            Ex. {"BTC": 20, "ETH": 20, "ADA": 20}
        :return: None
        """

        if not kwargs:
            return ValueError("orders cannot be null")

        self.orders = {}

        for product, amount in kwargs.items():
            self.orders[product] = amount

    def activate(self):
        """
        Activates the coinbase bot and performs transactions
        based on the dates and conditions.

        :return: None
        """

        print(f"Next deposit date: {self.next_deposit_date}")
        print(f"Next purchasing date: {self.next_purchase_date}")

        while True:

            # If our conditions are met, initiate transactions.
            if self.is_time_to_deposit():

                # Deposit from bank.
                deposit_amount = sum(self.orders.values())
                print(f"Depositing ${deposit_amount:.2f} into Coinbase Pro account. . .")
                self.coinbase.deposit_from_bank(deposit_amount)

                # Update to the next deposit date.
                self.update_deposit_date()

            if self.is_time_to_purchase():

                # Place market orders.
                for product, amount in self.orders.items():
                    print(f"Placing order for ${amount:.2f} of {product}. . .")
                    self.coinbase.place_market_order(product, amount)

                    try:
                        purchase_date = self.next_purchase_date.strftime("%Y-%m-%d")
                        transaction_details = self.coinbase.get_transaction_details(
                            product, purchase_date
                        )
                        if self.coinbase.send_email_confirmation(transaction_details):
                            print("Email confirmation sent!")

                    # There are no transaction details
                    except IndexError:
                        print("ERROR: Email could not be sent.")

                # Update to the next purchase date.
                self.update_purchase_date()

                # Print out the next deposit/purchase dates.
                print(f"Next deposit date: {self.next_deposit_date}")
                print(f"Next purchasing date: {self.next_purchase_date}")
