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

Now, you are able to configure your main() function in coinbase_bot.py
to your own specifications. At the moment, the main() function is set to
weekly purchases on Fridays at 10:00AM. Change these variables to your own
specifications:

            day_of_purchase = <day of the week>
            time_of_deposit = <time in format hh:mm with AM or PM appended>
            time_of_purchase = <time in format hh:mm with AM or PM appended>

Make sure time_of_deposit occurs before time_of_purchase otherwise, the market
orders will not go through.

If an order is successful, you can receive emails to notify you. To do this,
in your config.py file, add in the following:

                EMAIL_ADDRESS = ''
                EMAIL_PASSWORD = ''

You may need to adjust security settings on your email account for this.