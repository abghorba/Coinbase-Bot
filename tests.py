from config import CB_API_KEY_TEST, CB_API_SECRET_TEST, CB_API_PASS_TEST
from coinbase_bot import CoinbaseProHandler, CoinbaseExchangeAuth
import pytest


class TestCoinbaseProHandler():
    @pytest.mark.parametrize("product,amount", [
            (None, None),
            ("BTC", None),
            (None, 10.00),
            ("BTC", -5),
            ("BTC", -5.00),
            ("BTC", -5.01),
            ("BTC", 9.99),
            ("BTC", 100),
            ("BTC", 500.99),
            ("BTC", 1000.25),
            ("BTC", 2421.65),
            ("BTC", 3000)
    ])
    def test_place_market_order(self, product, amount):
        coinbase_pro = CoinbaseProHandler(
            api_url="https://api-public.sandbox.pro.coinbase.com/",
            auth=CoinbaseExchangeAuth(CB_API_KEY_TEST, CB_API_SECRET_TEST, CB_API_PASS_TEST)
        )

        result = coinbase_pro.place_market_order(product, amount)

        if product == "BTC" and (amount is not None and amount > 10.00):
            assert result
        else:
            assert result == False