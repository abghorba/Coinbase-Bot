# Coinbase Bot

<h2> Description </h2>
This bot is used to set up recurring purchases on Coinbase Pro.
Coinbase Pro does not currently offer recurring purchases.
This provides a way to Dollar Cost Average into cyptocurrencies.


<h2> Configuration </h2>
Install dependencies by calling

        pip install -r requirements.txt

You will need a Coinbase Pro account. You will also need to
create an API key via the Coinbase Pro website. Create your API key. 
Give the API key the View, Transfer, and Trade permissions. You will
also be given the following 3 pieces of information:

        key
        secret
        passphrase

Create a .env file from the provided .env.example file. Store this information
in the .env file in these variables:

        CB_API_KEY = ''
        CB_API_SECRET = ''
        CB_API_PASS = ''

In order to run tests, you must also fill out the credentials for the Coinbase Sandbox
API in the .env file as such:
                
        CB_API_KEY_TEST = ''
        CB_API_SECRET_TEST = ''
        CB_API_PASS_TEST = ''

To receive email confirmations of successful orders, fill out the following in your
.env file

        EMAIL_ADDRESS = ''
        EMAIL_PASSWORD = ''

You may need to adjust security settings on your email account for this.


<h2> Usage </h2>

Run the following command in your CLI to start the program:

                python coinbase_bot.py

You will be prompted for the following:

        1. Enter in the start date in format YYYY-MM-DD:
        2. Enter in the time you wish to conduct transactions in format HH:MM XM:
        3. How often would you like to make purchases? Valid values include "daily", "weekly", "biweekly", and "monthly":
        4. Enter in the cryprocurrency symbol you wish to purchase:
        5. Enter in the amount in USD to purchase with: 10
        6. Do you wish to add more orders? Y/N
                a. If Y, then repeat steps 4 - 6
                b. If N, then program will continue

The bot will sum the values in the orders and will deposit that amount into your Coinbase
Pro account. The market orders will be placed shortly after.

If you set up your email credentials correctly, you will be sent a confirmation once the
market order has been placed and filled.
