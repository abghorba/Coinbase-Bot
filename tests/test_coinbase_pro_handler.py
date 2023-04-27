from datetime import datetime

import pytest

from src.coinbase.coinbase_bot import CoinbaseExchangeAuth, CoinbaseProHandler
from src.coinbase.utilities import (
    CB_API_KEY_TEST,
    CB_API_PASS_TEST,
    CB_API_SECRET_TEST,
    EMAIL_ADDRESS,
    EMAIL_PASSWORD,
)

SANDBOX_API_URL = "https://api-public.sandbox.pro.coinbase.com/"
NONEMPTY_API_CREDENTIALS = (
    bool(CB_API_KEY_TEST) and bool(CB_API_PASS_TEST) and bool(CB_API_SECRET_TEST)
)
NONEMPTY_EMAIL_CREDENTIALS = bool(EMAIL_ADDRESS) and bool(EMAIL_PASSWORD)


class TestCoinbaseProHandler:
    valid_coinbase_auth = CoinbaseExchangeAuth(
        CB_API_KEY_TEST, CB_API_SECRET_TEST, CB_API_PASS_TEST
    )

    valid_coinbase_pro = CoinbaseProHandler(
        api_url=SANDBOX_API_URL, auth=valid_coinbase_auth
    )

    invalid_coinbase_auth = CoinbaseExchangeAuth("4096", "4096", "4096")

    invalid_coinbase_pro = CoinbaseProHandler(
        api_url=SANDBOX_API_URL, auth=invalid_coinbase_auth
    )

    todays_date = datetime.today().strftime("%Y-%m-%d")

    sample_valid_transaction_details = {
        "product": "BTC",
        "start_date": "2022-01-01",
        "coinbase_fee": ".10",
        "amount_invested": "10",
        "purchase_price": "100",
        "purchase_amount": "0.1",
        "total_amount": "9.90",
    }

    sample_invalid_transaction_details = {
        "product": "BTC",
        "start_date": "2022-01-01",
        "amount_invested": "10",
        "purchase_price": "100",
        "purchase_amount": "0.1",
        "total_amount": "9.90",
    }

    def test_get_payment_method_invalid_auth_raises_runtime_error(self):
        """Checks that payment method raises a RuntimeError if using invalid authorization"""

        with pytest.raises(RuntimeError, match="Could not find payment method"):
            self.invalid_coinbase_pro.get_payment_method()

    @pytest.mark.skipif(
        not NONEMPTY_API_CREDENTIALS, reason="No API credentials provided"
    )
    def test_get_payment_method_valid_auth(self):
        """Checks that get_payment_method() returns a nonempty string if using valid authorization"""

        assert self.valid_coinbase_pro.get_payment_method() != ""

    def test_deposit_from_bank_invalid_auth_raises_runtime_error(self):
        """Checks that depost_from_bank() raises a RuntimeError with invalid authorization"""

        with pytest.raises(RuntimeError, match="Could not find payment method"):
            self.invalid_coinbase_pro.deposit_from_bank(50)

    @pytest.mark.skip(reason="deposit_from_bank() is not supported in sandbox mode")
    @pytest.mark.skipif(
        not NONEMPTY_API_CREDENTIALS, reason="No API credentials provided"
    )
    def test_deposit_from_bank_valid_auth(self):
        """Checks that deposit_from_bank() returns True with valid authorization and parameters"""

        assert self.valid_coinbase_pro.deposit_from_bank(50)

    def test_deposit_from_bank_invalid_parameters(self):
        """Checks that deposit_from_bank() raises correct errors with invalid parameters"""

        with pytest.raises(TypeError, match="amount must be of type int or float"):
            self.invalid_coinbase_pro.deposit_from_bank(None)
            self.invalid_coinbase_pro.deposit_from_bank("50")
            self.invalid_coinbase_pro.deposit_from_bank("")

        with pytest.raises(ValueError, match="amount must be a positive number"):
            self.invalid_coinbase_pro.deposit_from_bank(0)
            self.invalid_coinbase_pro.deposit_from_bank(-0.01)

    def test_place_market_orders_invalid_auth_raises_runtime_error(self):
        """Checks place_market_order() raises a RuntimeError with invalid authorization."""

        with pytest.raises(RuntimeError, match="Could not place market order: "):
            self.invalid_coinbase_pro.place_market_order("BTC", 50)

    @pytest.mark.skipif(
        not NONEMPTY_API_CREDENTIALS, reason="No API credentials provided"
    )
    def test_place_market_order_valid_auth(self):
        """Checks place_marker_order() returns true with valid authorization and parameters."""

        assert self.valid_coinbase_pro.place_market_order("BTC", 50)

    def test_place_market_order_invalid_parameters(self):
        """Checks place_marker_order() returns appropriate error with invalid parameters."""

        with pytest.raises(TypeError, match="product must be of type str"):
            self.invalid_coinbase_pro.place_market_order(100, 100)
            self.invalid_coinbase_pro.place_market_order(None, 100)

        with pytest.raises(TypeError, match="amount must be of type int or float"):
            self.invalid_coinbase_pro.place_market_order("BTC", "100")
            self.invalid_coinbase_pro.place_market_order("BTC", "")
            self.invalid_coinbase_pro.place_market_order("BTC", None)

        with pytest.raises(ValueError, match="product cannot be null"):
            self.invalid_coinbase_pro.place_market_order("", 100)

        with pytest.raises(ValueError, match="amount must be a positive number"):
            self.invalid_coinbase_pro.place_market_order("BTC", 0)
            self.invalid_coinbase_pro.place_market_order("BTC", -0.01)

    def test_get_transaction_details_invalid_auth_raises_runtime_error(self):
        """Checks get_transaction_details() raises a RuntimeError with invalid authorization."""

        with pytest.raises(RuntimeError, match="Could not find transaction details"):
            self.invalid_coinbase_pro.get_transaction_details("BTC", self.todays_date)

    @pytest.mark.skipif(
        not NONEMPTY_API_CREDENTIALS, reason="No API credentials provided"
    )
    def test_get_transaction_details_valid_auth(self):
        """Checks that get_transaction_details() returns nonempty dict with valid authorization."""

        details = self.valid_coinbase_pro.get_transaction_details(
            "BTC", self.todays_date
        )
        assert bool(details)

    def test_get_transaction_details_invalid_parameters(self):
        """Checks get_transaction_details() raises appropriate errors with invalid parameters."""

        with pytest.raises(TypeError, match="product must be of type str"):
            self.invalid_coinbase_pro.get_transaction_details(100, "2022-01-01")
            self.invalid_coinbase_pro.get_transaction_details(None, "2022-01-01")

        with pytest.raises(TypeError, match="start_date must be of type str"):
            self.invalid_coinbase_pro.get_transaction_details("BTC", 100)
            self.invalid_coinbase_pro.get_transaction_details("BTC", None)

        with pytest.raises(ValueError, match="product cannot be null"):
            self.invalid_coinbase_pro.get_transaction_details("", "2022-01-01")

        with pytest.raises(ValueError, match="start_date cannot be null"):
            self.invalid_coinbase_pro.get_transaction_details("BTC", "")

        with pytest.raises(ValueError, match="does not match format"):
            self.invalid_coinbase_pro.get_transaction_details("BTC", "01/31/2022")
            self.invalid_coinbase_pro.get_transaction_details("BTC", "01-31-2022")
            self.invalid_coinbase_pro.get_transaction_details("BTC", "31/01/2022")

    @pytest.mark.skipif(
        NONEMPTY_EMAIL_CREDENTIALS, reason="Email credentials are provided"
    )
    def test_send_email_confirmation_invalid_email_credentials(self):
        """Checks if send_email_confirmation() return False with invalid email credentials."""

        assert not self.invalid_coinbase_pro.send_email_confirmation(
            self.sample_valid_transaction_details
        )

    @pytest.mark.skipif(
        not NONEMPTY_EMAIL_CREDENTIALS, reason="No email credentials provided"
    )
    def test_send_email_confirmation_valid_email_credentials(self):
        """Checks if send_email_confirmation() returns True with valid email credentials"""

        assert self.valid_coinbase_pro.send_email_confirmation(
            self.sample_valid_transaction_details
        )

    def test_send_email_confirmation_invalid_parameters(self):
        """Checks if send_email_confirmation() returns correct errors with invalid parameters."""

        with pytest.raises(TypeError, match="transaction_details must be of type dict"):
            self.invalid_coinbase_pro.send_email_confirmation(None)
            self.invalid_coinbase_pro.send_email_confirmation(100)
            self.invalid_coinbase_pro.send_email_confirmation("")

        with pytest.raises(ValueError, match="transaction_details cannot be null"):
            self.invalid_coinbase_pro.send_email_confirmation({})

        with pytest.raises(KeyError):
            self.invalid_coinbase_pro.send_email_confirmation(
                self.sample_invalid_transaction_details
            )
