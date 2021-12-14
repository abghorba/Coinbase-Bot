import datetime, json, hmac, hashlib, smtplib, time, requests, base64
from config import EMAIL_ADDRESS, EMAIL_PASSWORD
from email.message import EmailMessage
from requests.auth import AuthBase


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

 
FREQUENCY_TO_DAYS = {
    "daily": 1,
    "weekly": 7,
    "biweekly": 14,
    "monthly": 30
}

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
