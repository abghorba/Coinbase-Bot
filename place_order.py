from src.args.command_line_args import get_command_line_args
from src.coinbase.coinbase_bot import COINBASE_API_URL, CoinbaseBot, CoinbaseExchangeAuth
from src.coinbase.utilities import CoinbaseProCredentials
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

    coinbase_credentials = CoinbaseProCredentials()
    coinbase = CoinbaseBot(
        api_url=COINBASE_API_URL,
        auth=CoinbaseExchangeAuth(**vars(coinbase_credentials)),
        frequency=user_inputs.frequency,
        start_date=user_inputs.start_date,
        start_time=user_inputs.start_time,
    )

    coinbase.set_orders(**user_inputs.orders)

    try:
        print(coinbase.orders)
        coinbase.activate()

    except Exception as e:
        print(f"There was an error placing your order: {str(e)}")


if __name__ == "__main__":
    main()
