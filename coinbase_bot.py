import datetime, json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from config import CB_API_KEY, CB_API_SECRET, CB_API_PASS

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
            self.api_url + 'withdrawals/payment-method',
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


    def record_transaction(self, transaction_type, transaction_details):
        """
            Sends the current transaction's details into
            a database.
        
            :param transaction_type: The kind of transaction that occurred.
            :type transaction_type: str
            :param transaction_details: The JSON response of the transaction.
            :type transaction_details: JSON
            :return: None
        """

        pass


def main():

    # Initialize the CoinbaseProHandler object.
    coinbase_pro = CoinbaseProHandler(
        api_url="https://api.pro.coinbase.com/",
        auth=CoinbaseExchangeAuth(CB_API_KEY, CB_API_SECRET, CB_API_PASS)
    )

    # Set your variables. 
    # Make sure time_of_deposit occurs before time_of_purchase.
    day_of_purchase = "Friday"
    time_of_deposit = "9:55AM"
    time_of_purchase = "10:00AM"

    # Leave this running forever.
    while True:
        # Get the current day and time.
        now = datetime.datetime.now()
        current_day = now.strftime("%A")
        current_time = now.strftime("%I:%M%p")

        # If our conditions are met, initiate transactions.
        if current_day == day_of_purchase:
            if current_time == time_of_deposit:
                coinbase_pro.deposit_from_bank(50.00)
                time.sleep(60)
            elif current_time == time_of_purchase:
                coinbase_pro.place_market_order("ADA", 10.00)
                coinbase_pro.place_market_order("BTC", 20.00)
                coinbase_pro.place_market_order("ETH", 20.00)
                time.sleep(60)


if __name__ == "__main__":
    main()