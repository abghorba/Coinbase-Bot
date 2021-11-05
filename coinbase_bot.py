import json, hmac, hashlib, smtplib, time, requests, base64
from config import EMAIL_ADDRESS, EMAIL_PASSWORD
from email.message import EmailMessage
from requests.auth import AuthBase


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
        """
        Deposits USD from user's bank account
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
            print(f"Successfully deposited ${amount} to Coinbase Pro account.")
            success = True
        else:
            print("Could not make deposit to Coinbase Pro account.")
            print(response.content)

        return success


    def place_market_order(self, product, amount):
        """
        Places a market order for specified
        product with a specified amount of USD.

        Parameters
        ----------
        product : str
            The cryptocurrency to purchase. Valid values:
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
        """
        Retrieves the JSON response of the transaction details.

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

    
    def send_email_confirmation(self, transaction_details):
        """
        Send's user a confirmation email with
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