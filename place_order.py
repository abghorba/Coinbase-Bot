import datetime, time
from coinbase_bot import CoinbaseExchangeAuth, CoinbaseProHandler
from config import CB_API_KEY, CB_API_SECRET, CB_API_PASS


def main():
    # Configure your variables here.
    # time_of_deposit must occur BEFORE time_of_purchase.
    deposit_amount = 50.00
    day_of_purchase = "Friday"
    time_of_deposit = "10:10AM"
    time_of_purchase = "10:12AM"
    orders = {
        "BTC": 20.00,
        "ETH": 20.00,
        "SHIB": 10.00
    }

    # Initialize the CoinbaseProHandler object.
    coinbase_pro = CoinbaseProHandler(
        api_url="https://api.pro.coinbase.com/",
        auth=CoinbaseExchangeAuth(CB_API_KEY, CB_API_SECRET, CB_API_PASS)
    )

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
                print(f"Depositing ${deposit_amount:.2f} into Coinbase Pro account. . .")
                coinbase_pro.deposit_from_bank(deposit_amount)
                # Important to pause for 1 min so this doesn't repeat!
                time.sleep(60)
            elif current_time == time_of_purchase:
                # Place market orders.
                for product, amount in orders.items():
                    print(f"Placing order for ${amount:.2f} of {product}. . .")
                    coinbase_pro.place_market_order(product, amount)

                    # Pause to give time for the Coinbase API to update
                    # and store the transaction information.
                    time.sleep(3)
                    transaction_details = coinbase_pro.get_transaction_details(product, todays_date)
                    is_order_successful = coinbase_pro.send_email_confirmation(transaction_details)

                    if is_order_successful:
                        print("Email confirmation sent!")
                    else:
                        print("ERROR: Email could not be sent.")

                # Important to pause for 1 min so this doesn't repeat!
                time.sleep(60)
        
        # Delay execution of next iteration by 1 minute.
        time.sleep(60)

if __name__ == "__main__":
    main()