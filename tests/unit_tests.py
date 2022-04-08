import pytest

from config import CB_API_KEY_TEST, CB_API_SECRET_TEST, CB_API_PASS_TEST
from coinbase.coinbase_bot import CoinbaseBot, CoinbaseProHandler, CoinbaseExchangeAuth


SANDBOX_API_URL = "https://api-public.sandbox.pro.coinbase.com/"

class TestCoinbaseProHandler():

    coinbase_auth = CoinbaseExchangeAuth(CB_API_KEY_TEST, 
                                         CB_API_SECRET_TEST,
                                         CB_API_PASS_TEST)

    coinbase_pro = CoinbaseProHandler(api_url=SANDBOX_API_URL, 
                                      auth=coinbase_auth)

    @pytest.mark.parametrize(
        "product,amount,expected",
        [
            (None, None, False),
            ("BTC", None, False),
            (None, 10.00, False),
            ("BTC", -5, False),
            ("BTC", -0.01, False),
            ("BTC", 10.00, True),
            ("BTC", 1000, True),
            ("BTC", 10000000000, False),
        ],
    )
    def test_place_market_order(self, product, amount, expected):
        result = self.coinbase_pro.place_market_order(product, amount)
        assert result == expected
