from src.coinbase.coinbase_bot import COINBASE_API_URL, CoinbaseBot, CoinbaseExchangeAuth
from src.coinbase.utilities import CB_API_KEY, CB_API_PASS, CB_API_SECRET
from src.orders.command_line_input_collection import CommandLineInputCollector


def main():
    # Grab inputs from the user and check they are valid inputs.
    user_inputs = CommandLineInputCollector()
    user_inputs.collect_inputs()

    coinbase = CoinbaseBot(
        api_url=COINBASE_API_URL,
        auth=CoinbaseExchangeAuth(CB_API_KEY, CB_API_SECRET, CB_API_PASS),
        frequency=user_inputs.frequency,
        start_date=user_inputs.start_date,
        start_time=user_inputs.start_time,
    )

    coinbase.set_orders(**user_inputs.orders)

    try:
        coinbase.activate()
    except Exception:
        print("There was an error placing your order")


if __name__ == "__main__":
    main()
