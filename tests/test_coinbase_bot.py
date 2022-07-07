import pytest
import sys

from coinbase.coinbase_bot import CoinbaseBot
from coinbase.coinbase_bot import CoinbaseExchangeAuth
from coinbase.frequency import FREQUENCY_TO_DAYS
from config import CB_API_KEY_TEST
from config import CB_API_PASS_TEST
from config import CB_API_SECRET_TEST
from datetime import datetime
from datetime import timedelta
from threading import Thread
from time import sleep


SANDBOX_API_URL = "https://api-public.sandbox.pro.coinbase.com/"
NONEMPTY_API_CREDENTIALS = bool(CB_API_KEY_TEST) and bool(CB_API_PASS_TEST) and bool(CB_API_SECRET_TEST)


@pytest.mark.skipif(not NONEMPTY_API_CREDENTIALS, reason="No API credentials provided")
class TestCoinbaseBot():

    start_date = "2022-01-01"
    start_time = "10:00 AM"
    start_frequency = "weekly"
    first_purchase_date = datetime(2022, 1, 1, 10, 0)
    first_deposit_date = datetime(2022, 1, 1, 9, 59)
    
    purchase_date_plus_one_day = first_purchase_date + FREQUENCY_TO_DAYS["daily"]
    purchase_date_plus_one_week = first_purchase_date + FREQUENCY_TO_DAYS["weekly"]
    purchase_date_plus_two_weeks = first_purchase_date + FREQUENCY_TO_DAYS["biweekly"]
    purchase_date_plus_one_month = first_purchase_date + FREQUENCY_TO_DAYS["monthly"]

    deposit_date_plus_one_day = first_deposit_date + FREQUENCY_TO_DAYS["daily"]
    deposit_date_plus_one_week = first_deposit_date + FREQUENCY_TO_DAYS["weekly"]
    deposit_date_plus_two_weeks = first_deposit_date + FREQUENCY_TO_DAYS["biweekly"]
    deposit_date_plus_one_month = first_deposit_date + FREQUENCY_TO_DAYS["monthly"]

    todays_datetime = datetime.today().replace(second=0, microsecond=0)
    todays_date = todays_datetime.strftime('%Y-%m-%d')
    yesterdays_datetime = todays_datetime + timedelta(days=-1)
    tomorrows_datetime = todays_datetime + timedelta(days=1)

    todays_date_plus_thirty_seconds = todays_datetime + timedelta(seconds=30)
    todays_date_plus_one_minute = todays_datetime + timedelta(minutes=1)

    coinbase = CoinbaseBot(
        api_url=SANDBOX_API_URL,
        auth=CoinbaseExchangeAuth(CB_API_KEY_TEST, CB_API_SECRET_TEST, CB_API_PASS_TEST),
        frequency=start_frequency,
        start_date=start_date,
        start_time=start_time,
    )


    def test_parse_to_datetime_with_invalid_parameters(self):
        """Checks that parse_to_datetime() returns correct errors with invalid parameters."""

        with pytest.raises(TypeError, match="date must be of type str"):
            self.coinbase.parse_to_datetime(None, "10:00 AM")
            self.coinbase.parse_to_datetime(100, "10:00 AM")

        with pytest.raises(TypeError, match="time must be of type str"):
            self.coinbase.parse_to_datetime("2022-01-01", None)
            self.coinbase.parse_to_datetime("2022-01-01", 100)

        with pytest.raises(ValueError, match="date cannot be null"):
            self.coinbase.parse_to_datetime("", "10:00 AM")

        with pytest.raises(ValueError, match="time cannot be null"):
            self.coinbase.parse_to_datetime("2022-01-01", "")

        with pytest.raises(ValueError, match="does not match format"):
            self.coinbase.parse_to_datetime("01/31/2022", "10:00 AM")
            self.coinbase.parse_to_datetime("01-31-2022", "10:00 AM")
            self.coinbase.parse_to_datetime("2022-01-01", "10:00AM")
            self.coinbase.parse_to_datetime("2022-01-01", "10:00:00 AM")


    def test_parse_to_datetime(self):
        """Checks parse_to_datetime() parses datetimes correctly with valid parameters."""

        datetime_ = self.coinbase.parse_to_datetime("2022-01-01", "10:00 AM")
        expected_datetime = datetime(2022, 1, 1, 10, 0, 0)
        assert datetime_ == expected_datetime


    def test_update_frequency_with_invalid_parameters(self):
        """Checks update_frequency() raises correct errors with invalid parameters."""

        with pytest.raises(TypeError, match="ERROR: new_frequency must be of type str"):
            self.coinbase.update_frequency(None)
            self.coinbase.update_frequency(7)
        
        assert self.coinbase.time_delta == FREQUENCY_TO_DAYS[self.start_frequency]


    def test_update_frequency_invalid_frequency_raises_value_error(self):
        """Checks that invalid frequencies raise a ValueError."""

        with pytest.raises(ValueError, match="ERROR: invalid value for new_frequency"):
            self.coinbase.update_frequency("")
            self.coinbase.update_frequency("annually")

        assert self.coinbase.time_delta == FREQUENCY_TO_DAYS[self.start_frequency]


    @pytest.mark.parametrize(
        "new_frequency,expected_time_delta",
        [ 
            ("daily", FREQUENCY_TO_DAYS["daily"]),
            ("weekly", FREQUENCY_TO_DAYS["weekly"]),
            ("biweekly", FREQUENCY_TO_DAYS["biweekly"]),
            ("monthly", FREQUENCY_TO_DAYS["monthly"]),
        ]
    )
    def test_update_frequency(self, new_frequency, expected_time_delta):
        """Checks that valid frequencies change the time_delta attribute"""

        self.coinbase.update_frequency(new_frequency)
        assert self.coinbase.time_delta == expected_time_delta


    @pytest.mark.parametrize(
        "frequency,expected_date",
        [ 
            ("daily", deposit_date_plus_one_day),
            ("weekly", deposit_date_plus_one_week),
            ("biweekly", deposit_date_plus_two_weeks),
            ("monthly", deposit_date_plus_one_month)
        ]
    )
    def test_update_deposit_date(self, frequency, expected_date):
        """Checks that next_deposit_date updates according to current frequency"""

        self.coinbase.update_frequency(frequency)
        self.coinbase.update_deposit_date()
        assert self.coinbase.next_deposit_date == expected_date

        # Need to revert back to original deposit date
        self.coinbase.next_deposit_date = self.first_deposit_date


    def test_update_deposit_date_after_failed_frequency_change(self):
        """Checks that update_deposit_date() works correctly if we have a failed frequency change."""

        next_deposit_date = self.coinbase.next_deposit_date
        current_time_delta = self.coinbase.time_delta

        with pytest.raises(ValueError):
            self.coinbase.update_frequency("annually")

        self.coinbase.update_deposit_date()
        assert self.coinbase.next_deposit_date == (next_deposit_date + current_time_delta) 
       
        # Need to revert back to original deposit date
        self.coinbase.next_deposit_date = self.first_deposit_date


    @pytest.mark.parametrize(
        "frequency,expected_date",
        [ 
            ("daily", purchase_date_plus_one_day),
            ("weekly", purchase_date_plus_one_week),
            ("biweekly", purchase_date_plus_two_weeks),
            ("monthly", purchase_date_plus_one_month)
        ]
    )
    def test_update_purchase_date(self, frequency, expected_date):
        """Checks that next_purchase_date updates according to current frequency."""

        self.coinbase.update_frequency(frequency)
        self.coinbase.update_purchase_date()
        assert self.coinbase.next_purchase_date == expected_date

        # Need to revert back to original purchase date
        self.coinbase.next_purchase_date = self.first_purchase_date


    def test_update_purchase_date_after_failed_frequency_change(self):
        """Checks that update_purchase_date() works correctly after a failed frequency change."""
        
        next_purchase_date = self.coinbase.next_purchase_date
        current_time_delta = self.coinbase.time_delta

        with pytest.raises(ValueError):
            self.coinbase.update_frequency("annually")

        self.coinbase.update_purchase_date()
        assert self.coinbase.next_purchase_date == (next_purchase_date + current_time_delta) 

        # Need to revert back to original purchase date
        self.coinbase.next_purchase_date = self.first_purchase_date


    @pytest.mark.parametrize(
        "deposit_date,expected",
        [ 
            (yesterdays_datetime, False),
            (todays_datetime, True),
            (tomorrows_datetime, False)
        ]
    )
    def test_is_time_to_deposit(self, deposit_date, expected):
        """Checks if today is next_deposit_date"""
        
        self.coinbase.next_deposit_date = deposit_date
        assert self.coinbase.is_time_to_deposit() == expected

        # Need to revert back to original deposit date
        self.coinbase.next_deposit_date = self.first_deposit_date


    @pytest.mark.parametrize(
        "purchase_date,expected",
        [ 
            (yesterdays_datetime, False),
            (todays_datetime, True),
            (tomorrows_datetime, False)
        ]
    )
    def test_is_time_to_purchase(self, purchase_date, expected):
        """Checks if today is next_purchase_date"""
        
        self.coinbase.next_purchase_date = purchase_date
        assert self.coinbase.is_time_to_purchase() == expected

        # Need to revert back to original purchase date
        self.coinbase.next_purchase_date = self.first_purchase_date


    def test_set_orders_with_invalid_parameters(self):
        
        with pytest.raises(TypeError, match="set_orders\\(\\) takes 1 positional argument but 2 were given"):
            self.coinbase.set_orders()
            self.coinbase.set_orders(None)
            self.coinbase.set_orders("BTC")

        with pytest.raises(TypeError, match="set_orders\\(\\) argument after \\*\\* must be a mapping, not"):
            self.coinbase.set_orders(**"HI")
            self.coinbase.set_orders(**None)


    @pytest.mark.parametrize(
        "new_orders",
        [ 
            ({"BTC": 10}),
            ({"BTC": 20, "ETH": 20}),
            ({"BTC": 20, "ETH": 20, "ADA": 20}),
        ]
    )
    def test_set_orders(self, new_orders):
        """Checks that set_orders() changes orders attribute"""

        self.coinbase.set_orders(**new_orders)
        assert self.coinbase.orders == new_orders


    # Ensure that this test runs last!
    def test_activate(self):
        """Checks that the activate function works accordingly"""

        # Makes sure self.coinbase.activate() has enough time 
        # 2 minutes 30 seconds should be enough
        thread_timeout_seconds = 150

        for iteration, frequency in enumerate(FREQUENCY_TO_DAYS, 1):

            print("")
            print(f"Starting iteration {iteration} with frequency=\"{frequency}\"...")

            current_datetime = datetime.today().replace(second=0, microsecond=0)
    
            print(f"This iteration starts at time = {current_datetime}")

            current_datetime_plus_one_minute = current_datetime + timedelta(minutes=1)
            current_datetime_plus_two_minutes = current_datetime + timedelta(minutes=2)

            self.coinbase.next_deposit_date = current_datetime_plus_one_minute
            self.coinbase.next_purchase_date = current_datetime_plus_two_minutes

            current_deposit_date = self.coinbase.next_deposit_date
            current_purchase_date = self.coinbase.next_purchase_date

            self.coinbase.update_frequency(frequency)

            assert self.coinbase.time_delta == FREQUENCY_TO_DAYS[frequency]

            orders = {
                "BTC": iteration * 50,
            }

            self.coinbase.set_orders(**orders)

            # Create thread to do self.coinbase.activate() on first iteration
            if iteration == 1:
                t = Thread(target=self.coinbase.activate)
                t.daemon = True
                t.start()

            sleep(thread_timeout_seconds)

            assert self.coinbase.next_deposit_date == current_deposit_date + self.coinbase.time_delta
            assert self.coinbase.next_purchase_date == current_purchase_date + self.coinbase.time_delta
            