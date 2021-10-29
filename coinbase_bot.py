import datetime, json, hmac, hashlib, time, requests, base64, smtplib
from email.message import EmailMessage
from requests.auth import AuthBase
from config import CB_API_KEY, CB_API_SECRET, CB_API_PASS, EMAIL_ADDRESS, EMAIL_PASSWORD

# Create custom authentication for Exchange
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
        """
            Retrieves the user's bank from Coinbase Pro
            profile.

            :return: str or None
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
        """
            Deposits USD from user's bank account
            into their USD Wallet on Coinbase Pro.

            :param amount: The amount of USD to deposit.
            :type amount: float
            :return: bool
        
        """

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
            print(f"Successfully deposited ${amount} to Coinbase Pro account.")
            return True
        else:
            print("Could not make deposit to Coinbase Pro account.")
            print(response.content)
            return False


    def withdraw_to_bank(self, amount):
        """
            Withdraws the specified amount to the
            user's bank account.

            :param amount: The amount to be withdrawn.
            :type amount: float
            :return: bool
        """

        withdrawal_request = {
            "amount": amount,
            "curency": "USD",
            "payment_method_id": self.get_payment_method()
        }

        response = requests.post(
            self.api_url + 'withdrawals/payment-method',
            data=json.dumps(withdrawal_request),
            auth=self.auth
        )

        if response:
            print(f"Successfully withdrew ${amount} to bank.")
            return True
        else:
            print("Could not make withdrawal to bank.")
            print(response.content)
            return False


    def place_market_order(self, product, amount):
        """
            Places a market order for specified
            product with a specified amount of USD.

            :param product: The cryptocurrency to purchase.
            :type product: str
            :param amount: The amount of USD to purchase with.
            :type amount: float
            :return: bool
        
        """

        if not product:
            print("Please specify product.")
            return False
        elif not amount:
            print("Please specify amount.")
            return False

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
            return True
        else:
            print("Could not place market order.")
            print(response.content)
            return False


    def get_transaction_details(self, product, start_date):
        """
            Retrieves the JSON response of the transaction details.

            :param product: The cyptocurrency in question.
            :type product: str
            :param start_date: The date the transaction took place.
            :type start_date: str in "yyyy-mm-dd" format
            :returns: dictionary of parsed JSON responses

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
        print(response.json())
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


def send_email_confirmation(transaction_details):
    """
        Send's user an email with transaction details.

        :param transaction_details: Dictionary of transaction details
        :type transaction_details: dict
        :returns: None

    """

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


def main():

    # Initialize the CoinbaseProHandler object.
    coinbase_pro = CoinbaseProHandler(
        api_url="https://api.pro.coinbase.com/",
        auth=CoinbaseExchangeAuth(CB_API_KEY, CB_API_SECRET, CB_API_PASS)
    )

    # Set your variables. 
    # Make sure time_of_deposit occurs before time_of_purchase.
    deposit_amount = 60.00
    day_of_purchase = "Friday"
    time_of_deposit = "10:00AM"
    time_of_purchase = "10:02AM"
    purchase_amounts = {
        "BTC": 20.00,
        "ETH": 20.00,
        "ADA": 10.00,
        "SHIB": 10.00
    }

    # Leave this running forever.
    while True:
        # Get the current day and time.
        now = datetime.datetime.now()
        current_day = now.strftime("%A")
        current_time = now.strftime("%I:%M%p")
        todays_date = now.isoformat()[:10]

        # If our conditions are met, initiate transactions.
        if current_day == day_of_purchase:
            if current_time == time_of_deposit:
                # Deposit from bank.
                print("depositing. . . . .")
                coinbase_pro.deposit_from_bank(deposit_amount)
                # Important to pause for >1 min so this doesn't repeat!
                time.sleep(60)
            elif current_time == time_of_purchase:
                # Place market orders.
                for product, amount in purchase_amounts.items():
                    print(f"Placing order for {product}...")
                    coinbase_pro.place_market_order(product, amount)

                    # Pause between placing the order and sending email
                    # this will give time for the Coinbase API to update
                    # and store the transaction information.
                    time.sleep(3)
                    transaction_details = coinbase_pro.get_transaction_details(product, todays_date)
                    send_email_confirmation(transaction_details)

                # Important to pause for >1 min so this doesn't repeat!
                time.sleep(60)


if __name__ == "__main__":
    main()