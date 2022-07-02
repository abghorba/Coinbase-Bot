import pytest

from coinbase.coinbase_bot import CoinbaseExchangeAuth
from coinbase.coinbase_bot import CoinbaseProHandler
from config import CB_API_KEY_TEST
from config import CB_API_PASS_TEST
from config import CB_API_SECRET_TEST
from config import EMAIL_ADDRESS
from config import EMAIL_PASSWORD
from datetime import datetime


SANDBOX_API_URL = "https://api-public.sandbox.pro.coinbase.com/"
NONEMPTY_API_CREDENTIALS = bool(CB_API_KEY_TEST) and bool(CB_API_PASS_TEST) and bool(CB_API_SECRET_TEST)
NONEMPTY_EMAIL_CREDENTIALS = bool(EMAIL_ADDRESS) and bool(EMAIL_PASSWORD) 


class TestCoinbaseProHandler():

    valid_coinbase_auth = CoinbaseExchangeAuth(CB_API_KEY_TEST, 
                                               CB_API_SECRET_TEST,
                                               CB_API_PASS_TEST)

    valid_coinbase_pro = CoinbaseProHandler(api_url=SANDBOX_API_URL, 
                                            auth=valid_coinbase_auth)

    invalid_coinbase_auth = CoinbaseExchangeAuth("4096", 
                                                 "4096",
                                                 "4096")

    invalid_coinbase_pro = CoinbaseProHandler(api_url=SANDBOX_API_URL, 
                                              auth=invalid_coinbase_auth)

    todays_date = datetime.today().strftime('%Y-%m-%d')


    def test_get_payment_method_invalid_auth(self):
        payment_id = self.invalid_coinbase_pro.get_payment_method()
        assert payment_id == ""

    @pytest.mark.skipif(not NONEMPTY_API_CREDENTIALS, reason="No API credentials provided")
    def test_get_payment_method_valid_auth(self):
        payment_id = self.valid_coinbase_pro.get_payment_method()
        assert payment_id != ""

    @pytest.mark.parametrize(
        "amount,expected",
        [
            ("1", False),
            (-1, False),
            (0, False),
            (50, False),
        ]
    )
    def test_deposit_from_bank_invalid_auth(self, amount, expected):
        success = self.invalid_coinbase_pro.deposit_from_bank(amount)
        assert success == expected

    @pytest.mark.skipif(not NONEMPTY_API_CREDENTIALS, reason="No API credentials provided")
    @pytest.mark.parametrize(
        "amount,expected",
        [
            ("1", False),
            (-1, False),
            (0, False),
            (50, False),
        ]
    )
    def test_deposit_from_bank_valid_auth(self, amount, expected):
        success = self.valid_coinbase_pro.deposit_from_bank(amount)
        assert success == expected


    @pytest.mark.parametrize(
        "product,amount,expected",
        [
            # Invalid Parameters
            (None, None, False),
            ("BTC", None, False),
            (None, 10.00, False),
            ("BTC", -5, False),
            ("BTC", -0.01, False),
            ("BTC", 10000000000, False),

            # Valid Parameters
            ("BTC", 10.00, False),
            ("BTC", 1000, False),
        ],
    )
    def test_place_market_orders_invalid_auth(self, product, amount, expected):
        result = self.invalid_coinbase_pro.place_market_order(product, amount)
        assert result == expected

    @pytest.mark.skipif(not NONEMPTY_API_CREDENTIALS, reason="No API credentials provided")
    @pytest.mark.parametrize(
        "product,amount,expected",
        [
            # Invalid Parameters
            (None, None, False),
            ("BTC", None, False),
            (None, 10.00, False),
            ("BTC", -5, False),
            ("BTC", -0.01, False),
            ("BTC", 10000000000, False),

            # Valid Parameters
            ("BTC", 10.00, True),
            ("BTC", 1000, True),
        ],
    )
    def test_place_market_order_valid_auth(self, product, amount, expected):
        result = self.valid_coinbase_pro.place_market_order(product, amount)
        assert result == expected

    def test_get_transaction_details_invalid_auth(self):
        details = self.invalid_coinbase_pro.get_transaction_details("BTC", self.todays_date)
        assert not bool(details)

    @pytest.mark.skipif(not NONEMPTY_API_CREDENTIALS, reason="No API credentials provided")
    def test_get_transaction_details_valid_auth(self):
        details = self.invalid_coinbase_pro.get_transaction_details("BTC", self.todays_date)
        print(details)
        assert bool(details)

    @pytest.mark.skipif(NONEMPTY_EMAIL_CREDENTIALS, reason="Email credentials are provided")
    def test_send_email_confirmation_invalid_email_credentials(self):
        transaction_details = {
            "product": "BTC",
            "start_date": "2022-01-01",
            "coinbase_fee": ".10",
            "amount_invested": "10",
            "purchase_price": "100",
            "purchase_amount": "0.1",
            "total_amount": "9.90"
        }
        success = self.invalid_coinbase_pro.send_email_confirmation(transaction_details)
        assert not success

    @pytest.mark.skipif(not NONEMPTY_EMAIL_CREDENTIALS, reason="No email credentials provided")
    def test_send_email_confirmation_valid_email_credentials(self):
        transaction_details = {
            "product": "BTC",
            "start_date": "2022-01-01",
            "coinbase_fee": ".10",
            "amount_invested": "10",
            "purchase_price": "100",
            "purchase_amount": "0.1",
            "total_amount": "9.90"
        }
        success = self.valid_coinbase_pro.send_email_confirmation(transaction_details)
        assert success
