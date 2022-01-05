from ctypes import create_unicode_buffer
import datetime, json, hmac, hashlib, smtplib, time, requests, base64
from config import EMAIL_ADDRESS, EMAIL_PASSWORD
from email.message import EmailMessage
from requests.auth import AuthBase


FREQUENCY_TO_DAYS = {
    "daily": 1,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30
}

class InputCollector():
    def __init__(self):
        self.start_date_is_today = False

    def get_start_date(self):
        """Checks if the start date the user inputs is valid.

        Parameters
        ----------
        None

        Returns
        -------
        date : str
            The date string in format YYYY-MM-DD.
        
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
                converted_date = datetime.datetime.strptime(date, format)
                # year, month, day = date.split("-")
                # converted_date = datetime(year=int(year), month=int(month), day=int(day))
            except ValueError:
                print("This date does not exist!")
                continue
            
            # Make sure the date isn't before the current day
            current_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if converted_date < current_date:
                print("The date must occur on or after the current date.")
                continue

            # Need to know if today is the start date for time validation
            if converted_date == current_date:
                self.start_date_is_today = True

            valid_date = True
        
        return date


    def get_start_time(self):
        """Checks if the start date the user inputs is valid.

        Parameters
        ----------
        time : str
            The time string in format HH:MM XM.

        Returns
        -------
        start_time : str
            The time in format HH:MM XM.
        
        """
        valid_start_time = False
        
        while not valid_start_time:
            start_time = input("Enter in the time you wish to conduct transactions in format HH:MM XM: ")

            # Null check
            if not start_time:
                raise TypeError("Time cannot be null.")
                continue

            # Make sure its a valid time
            try:
                format = "%I:%M %p"
                converted_time = datetime.datetime.strptime(start_time, format).time()
            except ValueError:
                print("This is not a valid time.")
                continue

            # If the start date is today, the time must occur after the current time.
            if self.start_date_is_today:
                current_time = datetime.datetime.now().time()
                if converted_time < current_time:
                    print("The chosen start date is today. The time of the transaction must occur after the current time.")
                    continue
            
            valid_start_time = True

        return start_time

            
    def get_frequency(self):
        """Checks if the frequency the user inputs is valid.

        Parameters
        ----------
        None

        Returns
        -------
        frequency : str
            The frequency of the transactions.
        
        """
        valid_frequency = False

        while not valid_frequency:
            frequency = input("How often would you like to make purchases? Valid values include \"daily\", \"weekly\", \"biweekly\", and \"monthly\": ")

            # Null check
            if not frequency:
                print("Frequency cannot be null.")
                continue

            # Check frequency is valid
            if frequency.lower() in FREQUENCY_TO_DAYS:
                valid_frequency = True
            else:
                print("Invalid value. Valid values include \"daily\", \"weekly\", \"biweekly\", and \"monthly\".")

        return frequency


    def get_orders(self):
        """Constructs a dictionary of each order.
        
        Parameters
        ----------
        None

        Returns
        -------
        orders : dict
            A dictionary with key value pair
            "crypto" : dollar_amount

        """
        valid_orders = False
        base_url = "https://api.exchange.coinbase.com/currencies/"
        orders = {}

        while not valid_orders:
            # Grab the crypto symbol first
            valid_crypto = False
            while not valid_crypto:
                crypto = input("Enter in the cryprocurrency symbol you wish to purchase: ")
                crypto = crypto.upper()

                # There is already a pending order for the inputted cryptocurrency
                if crypto in orders:
                    overwrite_order = input("There is already a pending order for this cryptocurrency. Continuing will overwrite the previous order. Continue? Y/N ")
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


# Create custom authentication for Exchange.
class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message.encode(), hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode()

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


# Create custom handler for placing orders.
class CoinbaseProHandler():
    def __init__(self, api_url, auth):
        self.api_url = api_url
        self.auth = auth


    def get_payment_method(self):
        """Retrieves the user's bank from Coinbase Pro
        profile.

        Parameters
        ----------
        None

        Returns
        -------
        payment_id : str or None
            The user's bank ID.
        """
        response = requests.get(
            self.api_url + 'payment-methods', 
            auth=self.auth
        )

        if response:
            print("Successfully retrieved payment method.")
            payment_id = response.json()[0]['id']
            return payment_id
        else:
            print("Could not find payment method.")
            print(response.content)


    def deposit_from_bank(self, amount):
        """Deposits USD from user's bank account
        into their USD Wallet on Coinbase Pro.

        Parameters
        ----------
        amount : float
            The amount of USD to deposit.

        Returns
        -------
        success : bool
            True if the deposit is successful. 
        """
        success = False

        deposit_request = {
            'amount': amount,
            'currency': 'USD',
            'payment_method_id': self.get_payment_method()
        }

        response = requests.post(
            self.api_url + 'deposits/payment-method',
            data=json.dumps(deposit_request),
            auth=self.auth
        )

        if response:
            print(f"Successfully deposited ${amount:.2f} to Coinbase Pro account.")
            success = True
        else:
            print("Could not make deposit to Coinbase Pro account.")
            print(response.content)

        return success


    def place_market_order(self, product, amount):
        """Places a market order for specified
        product with a specified amount of USD.

        Parameters
        ----------
        product : str
            The cryptocurrency to purchase.
        amount : float
            The amount of USD to make a purchase with.

        Returns
        -------
        success : boolean
            True if the market order is successfully executed.
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
            "funds": amount
        }

        response = requests.post(
            self.api_url + 'orders',
            data=json.dumps(market_order),
            auth=self.auth
        )

        if response:
            print(f"Successfully made a market order for ${amount} of {product}.")
            success = True
        else:
            print("Could not place market order.")
            print(response.content)
        
        return success


    def get_transaction_details(self, product, start_date):
        """Retrieves the JSON response of the transaction details.

        Parameters
        ----------
        product : str
            The cyptocurrency to get transaction details of.
        start_date: str
            String in "yyyy-mm-dd" format.

        Returns
        -------
        parsed_transaction : dict
            Extracted details from the retrieved JSON.
        """
        fill_parameters = {
            "product_id": product + "-USD",
            "start_date": start_date
        }

        response = requests.get(
            self.api_url + "fills",
            params=fill_parameters,
            auth=self.auth
        )

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
            "total_amount": "%.2f" % (coinbase_fee + amount_invested)
        }

        return parsed_transaction

    
    def send_email_confirmation(self, transaction_details):
        """Send's user a confirmation email with
        the details of the transaction.  

        Parameters
        ----------
        transaction_details : str
            Dictionary of transaction details.

        Returns
        -------
        success : bool
            True if the email is sent successfully.     
        """
        success = False

        if not transaction_details:
            return success

        product = transaction_details["product"]
        start_date = transaction_details["start_date"]
        coinbase_fee = transaction_details["coinbase_fee"]
        amount_invested = transaction_details["amount_invested"]
        purchase_price = transaction_details["purchase_price"]
        purchase_amount = transaction_details["purchase_amount"]
        total_amount = transaction_details["total_amount"]

        msg = EmailMessage()
        msg['Subject'] = f"Your Purchase of ${total_amount} of {product} Was Successful!"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS

        content = f'Hello,\n\n You successfully placed your order! Please see below details:\n\n \
            Amount Purchased: {purchase_amount} {product}\n \
            Purchase Price: ${purchase_price}\n \
            Total Amount: ${total_amount}\n \
            Amount Invested: ${amount_invested}\n \
            Coinbase Fees: ${coinbase_fee}\n \
            Date: {start_date}'

        msg.set_content(content)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            success = True
        
        return success


class CoinbaseBot():
    def __init__(self, api_url, auth, frequency, start_date, start_time):
        self.coinbase = CoinbaseProHandler(api_url, auth)
        self.time_delta = FREQUENCY_TO_DAYS[frequency]
        self.next_purchase_date = self.parse_to_datetime(start_date, start_time)
        self.next_deposit_date = self.next_purchase_date + datetime.timedelta(minutes=-1)
        self.orders = {}


    def parse_to_datetime(self, date, time):
        """Parses both a date string and a time string into one datetime
        object.

        Parameters
        ----------
        date : str
            The date string in format YYYY-MM-DD.
        time : str
            The time string in format HH:MM XM.

        Returns
        -------
        date_and_time : datetime
            A datetime object representing the passed in date and time
            strings.
        """
        date_and_time = date + " " + time
        format = "%Y-%m-%d %I:%M %p"
        date_and_time = datetime.datetime.strptime(date_and_time, format)
        return date_and_time


    def update_frequency(self, new_frequency):
        """Updates the frequency of the purchases.

        Parameters
        ----------
        new_frequency : str
            Valid values are "daily", "weekly", "biweekly", "monthly".

        Returns
        -------
        None
        """
        if new_frequency not in FREQUENCY_TO_DAYS:
            print("ERROR: Invalid value for new_frequency.")
        self.time_delta = FREQUENCY_TO_DAYS[new_frequency]


    def update_deposit_date(self):
        """Updates to the next deposit date."""
        self.next_deposit_date += datetime.timedelta(self.time_delta)


    def update_purchase_date(self):
        """Updates to the next purchase date."""
        self.next_purchase_date += datetime.timedelta(self.time_delta)


    def is_time_to_deposit(self):
        """Returns True if the current datetime is the deposit datetime."""
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        return now == self.next_deposit_date


    def is_time_to_purchase(self):
        """Returns True if current datetime is the purchase datetime."""
        now = datetime.datetime.now().replace(second=0, microsecond=0)
        return now == self.next_purchase_date


    def set_orders(self, **kwargs):
        """Sets the orders for recurring purchases.

        Parameters
        ----------
        dict
            Any number of key-value pairs for product to amount.
            Ex. {"BTC": 20, "ETH": 20, "ADA": 20}
        
        Returns
        -------
        None
        """
        self.orders = {}
        for product, amount in kwargs.items():
            self.orders[product] = amount


    def activate(self):
        """Activates the coinbase bot and performs transactions
        based on the dates and conditions.

        Parameters
        ----------
        None

        Returns
        -------
        None
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

                    # Pause to give time for the Coinbase API to update
                    # and store the transaction information.
                    time.sleep(10)
                    try:
                        purchase_date = self.next_purchase_date.strftime("%Y-%m-%d")
                        transaction_details = self.coinbase.get_transaction_details(product, purchase_date)
                        self.coinbase.send_email_confirmation(transaction_details)
                        print("Email confirmation sent!")
                    except IndexError: # If there are no transaction details.
                        print("ERROR: Email could not be sent.")

                # Update to the next purchase date.
                self.update_purchase_date()

                # Print out the next deposit/purchase dates.
                print(f"Next deposit date: {self.next_deposit_date}")
                print(f"Next purchasing date: {self.next_purchase_date}")
