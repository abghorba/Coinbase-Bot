from src.coinbase.utilities import CB_API_KEY
from src.coinbase.utilities import CB_API_PASS
from src.coinbase.utilities import CB_API_SECRET
from src.coinbase.coinbase_bot import CoinbaseBot
from src.coinbase.coinbase_bot import CoinbaseExchangeAuth
from src.coinbase.coinbase_bot import COINBASE_API_URL
from src.coinbase.input_collection import InputCollector


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

    try:
        coinbase.activate()
    except Exception:
        print("There was an error placing your order")


if __name__ == "__main__":
    main()
