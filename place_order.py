from coinbase_bot import CoinbaseExchangeAuth, CoinbaseBot, InputCollector
from config import CB_API_KEY, CB_API_SECRET, CB_API_PASS


def main():
    # Grab inputs from the user and check they are valid inputs.
    user_inputs = InputCollector()
    user_inputs.collect_inputs()

    coinbase = CoinbaseBot(
        api_url="https://api.pro.coinbase.com/",
        auth=CoinbaseExchangeAuth(CB_API_KEY, CB_API_SECRET, CB_API_PASS),
        frequency=user_inputs.frequency,
        start_date=user_inputs.start_date,
        start_time=user_inputs.start_time,
    )

    coinbase.set_orders(**user_inputs.orders)

    coinbase.activate()


if __name__ == "__main__":
    main()
