# Coinbase Bot

<h2> Description </h2>
This bot is used to set up recurring purchases on Coinbase Pro.
Coinbase Pro does not currently offer recurring purchases.
This provides a way to Dollar Cost Average into cyptocurrencies.

<h2> Usage </h2>
Install dependencies by calling

        pip install -r requirements.txt

You will need a Coinbase Pro account. You will also need to
create an API key via the Coinbase Pro website. Create your API key. 
Give the API key the View, Transfer, and Trade permissions. You will
also be given the following 3 pieces of information:

        key
        secret
        passphrase

Store this information in a config.py file like so:

        CB_API_KEY = ''
        CB_API_SECRET = ''
        CB_API_PASS = ''

Now, you are able to configure your main() function in place_order.py
to your own specifications. 
You can change the frequency to "daily", "weekly", "biweekly", or "monthly".
You can change start_date to whatever, as long as the format is YYYY-MM-DD.
You can change start_time to whatever, as long as the format is HH:MM XM.

        coinbase = CoinbaseBot(
                api_url="https://api.pro.coinbase.com/",
                auth=CoinbaseExchangeAuth(CB_API_KEY, CB_API_SECRET, CB_API_PASS),
                frequency="biweekly",
                start_date="2021-11-19",
                start_time="10:00 AM"
                )


Now, you will need to set your orders. You can do this by manipulating the following
in main() on place_order.py. The key will be the cryptocurrency to buy, and the value
will be the amount to purchase.

        coinbase.set_orders(**{
                "BTC": 20,
                "ETH": 30,
        })


The bot will sum the values in the orders and will deposit that amount into your Coinbase
Pro account. The market orders will be placed shortly after.

If an order is successful, you will receive an email to notify you. To configure this,
in your config.py file, add in the following:

                EMAIL_ADDRESS = ''
                EMAIL_PASSWORD = ''

You may need to adjust security settings on your email account for this.