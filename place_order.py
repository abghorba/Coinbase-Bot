import os

from config import CB_API_KEY, CB_API_SECRET, CB_API_PASS
from coinbase.coinbase_bot import CoinbaseExchangeAuth, CoinbaseBot
from coinbase.input_collection import InputCollector


COINBASE_API_URL = "https://api.pro.coinbase.com/"


def main():

    # Grab inputs from the user and check they are valid inputs.
    user_inputs = InputCollector()
    user_inputs.collect_inputs()
    
    coinbase = CoinbaseBot(
        api_url=COINBASE_API_URL,
        auth=CoinbaseExchangeAuth(CB_API_KEY, CB_API_SECRET, CB_API_PASS),
        frequency=user_inputs.frequency,
        start_date=user_inputs.start_date,
        start_time=user_inputs.start_time,
    )

    coinbase.set_orders(**user_inputs.orders)

    coinbase.activate()


if __name__ == "__main__":
    main()
