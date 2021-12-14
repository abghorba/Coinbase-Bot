from coinbase_bot import CoinbaseExchangeAuth, CoinbaseBot
from config import CB_API_KEY, CB_API_SECRET, CB_API_PASS

def main():
    coinbase = CoinbaseBot(
            api_url="https://api.pro.coinbase.com/",
            auth=CoinbaseExchangeAuth(CB_API_KEY, CB_API_SECRET, CB_API_PASS),
            frequency="weekly",
            start_date="2021-12-17",
            start_time="10:00 AM"
        )

    coinbase.set_orders(**{
        "BTC": 20,
        "ETH": 30,
    })

    coinbase.activate()

if __name__ == "__main__":
    main()