from config import CB_API_KEY_TEST, CB_API_SECRET_TEST, CB_API_PASS_TEST
from coinbase_bot import CoinbaseBot, CoinbaseProHandler, CoinbaseExchangeAuth
import pytest


class TestCoinbaseProHandler():
    coinbase_pro = CoinbaseProHandler(
            api_url="https://api-public.sandbox.pro.coinbase.com/",
            auth=CoinbaseExchangeAuth(CB_API_KEY_TEST, CB_API_SECRET_TEST, CB_API_PASS_TEST)
        )

    @pytest.mark.parametrize("product,amount,expected", [
            (None, None, False),
            ("BTC", None, False),
            (None, 10.00, False),
            ("BTC", -5, False),
            ("BTC", -0.01, False),
            ("BTC", 10.00, True),
            ("BTC", 1000, True),
            ("BTC", 10000000000, False),
    ])
    def test_place_market_order(self, product, amount, expected):
        result = self.coinbase_pro.place_market_order(product, amount)
        assert result == expected