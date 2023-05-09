from src.args.command_line_args import get_command_line_args
from src.coinbase.coinbase_bot import COINBASE_API_URL, CoinbaseBot, CoinbaseExchangeAuth
from src.coinbase.utilities import CB_API_KEY, CB_API_PASS, CB_API_SECRET
from src.orders.command_line_input_collector import CommandLineInputCollector
from src.orders.yaml_input_collector import YAMLInputCollector


def main():
    cli_args = get_command_line_args()

    # User chose to input orders via yaml file
    if cli_args["yaml"]:
        user_inputs = YAMLInputCollector()

    # Default to inputting orders via the command line
    else:
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
        print(coinbase.orders)
        coinbase.activate()
    except Exception:
        print("There was an error placing your order")


if __name__ == "__main__":
    main()
