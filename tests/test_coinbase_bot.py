import pytest

from coinbase.coinbase_bot import CoinbaseBot
from coinbase.coinbase_bot import CoinbaseExchangeAuth
from coinbase.frequency import FREQUENCY_TO_DAYS
from config import CB_API_KEY_TEST
from config import CB_API_PASS_TEST
from config import CB_API_SECRET_TEST
from datetime import datetime
from datetime import timedelta
from threading import Thread
from threading import Timer
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

    todays_date_plus_one_minute = todays_datetime + timedelta(minutes=1)

    coinbase = CoinbaseBot(
        api_url=SANDBOX_API_URL,
        auth=CoinbaseExchangeAuth(CB_API_KEY_TEST, CB_API_SECRET_TEST, CB_API_PASS_TEST),
        frequency=start_frequency,
        start_date=start_date,
        start_time=start_time,
    )

    # @pytest.mark.parametrize(
    #     "date,time",
    #     [ 
    #         (None, "10:00 AM"),
    #         ("", "10:00 AM"),
    #         ("2022-01-01", None),
    #         ("2022-01-01", ""),
    #         ("2022/01/01", "10:00AM"),
    #     ]
    # )
    # def test_parse_to_datetime_raises_value_error(self, date, time):
    #     with pytest.raises(ValueError):
    #         self.coinbase.parse_to_datetime(date, time)

    # def test_parse_to_datetime(self):
    #     datetime_ = self.coinbase.parse_to_datetime("2022-01-01", "10:00 AM")
    #     expected_datetime = datetime(2022, 1, 1, 10, 0, 0)
    #     assert datetime_ == expected_datetime

    # @pytest.mark.parametrize(
    #     "new_frequency",
    #     [ 
    #         ("annually"),
    #         ("quarterly"),
    #         ("hourly"),
    #     ]
    # )
    # def test_update_frequency_raises_value_error(self, new_frequency):
    #     """Checks that invalid frequencies raises a ValueError"""

    #     with pytest.raises(ValueError):
    #         self.coinbase.update_frequency(new_frequency)

    #     assert self.coinbase.time_delta == FREQUENCY_TO_DAYS[self.start_frequency]

    # @pytest.mark.parametrize(
    #     "new_frequency,expected",
    #     [ 
    #         ("daily", FREQUENCY_TO_DAYS["daily"]),
    #         ("weekly", FREQUENCY_TO_DAYS["weekly"]),
    #         ("biweekly", FREQUENCY_TO_DAYS["biweekly"]),
    #         ("monthly", FREQUENCY_TO_DAYS["monthly"]),
    #     ]
    # )
    # def test_update_frequency(self, new_frequency, expected):
    #     """Checks that valid frequencies change the time_delta attribute"""

    #     self.coinbase.update_frequency(new_frequency)
    #     assert self.coinbase.time_delta == expected

    # @pytest.mark.parametrize(
    #     "frequency,expected_date",
    #     [ 
    #         ("daily", deposit_date_plus_one_day),
    #         ("weekly", deposit_date_plus_one_week),
    #         ("biweekly", deposit_date_plus_two_weeks),
    #         ("monthly", deposit_date_plus_one_month)
    #     ]
    # )
    # def test_update_deposit_date(self, frequency, expected_date):
    #     """Checks that next_deposit_date updates according to current frequency"""

    #     self.coinbase.update_frequency(frequency)
    #     self.coinbase.update_deposit_date()
    #     assert self.coinbase.next_deposit_date == expected_date

    #     # Need to revert back to original deposit date
    #     self.coinbase.next_deposit_date = self.first_deposit_date

    # @pytest.mark.parametrize(
    #     "frequency,expected_date",
    #     [ 
    #         ("daily", purchase_date_plus_one_day),
    #         ("weekly", purchase_date_plus_one_week),
    #         ("biweekly", purchase_date_plus_two_weeks),
    #         ("monthly", purchase_date_plus_one_month)
    #     ]
    # )
    # def test_update_purchase_date(self, frequency, expected_date):
    #     """Checks that next_purchase_date updates according to current frequency"""

    #     self.coinbase.update_frequency(frequency)
    #     self.coinbase.update_purchase_date()
    #     assert self.coinbase.next_purchase_date == expected_date

    #     # Need to revert back to original purchase date
    #     self.coinbase.next_purchase_date = self.first_purchase_date

    # @pytest.mark.parametrize(
    #     "deposit_date,expected",
    #     [ 
    #         (yesterdays_datetime, False),
    #         (todays_datetime, True),
    #         (tomorrows_datetime, False)
    #     ]
    # )
    # def test_is_time_to_deposit(self, deposit_date, expected):
    #     """Checks if today is next_deposit_date"""
        
    #     self.coinbase.next_deposit_date = deposit_date
    #     assert self.coinbase.is_time_to_deposit() == expected

    #     # Need to revert back to original deposit date
    #     self.coinbase.next_deposit_date = self.first_deposit_date

    # @pytest.mark.parametrize(
    #     "purchase_date,expected",
    #     [ 
    #         (yesterdays_datetime, False),
    #         (todays_datetime, True),
    #         (tomorrows_datetime, False)
    #     ]
    # )
    # def test_is_time_to_purchase(self, purchase_date, expected):
    #     """Checks if today is next_purchase_date"""
        
    #     self.coinbase.next_purchase_date = purchase_date
    #     assert self.coinbase.is_time_to_purchase() == expected

    #     # Need to revert back to original purchase date
    #     self.coinbase.next_purchase_date = self.first_purchase_date

    # @pytest.mark.parametrize(
    #     "new_orders",
    #     [ 
    #         ({"BTC": 10}),
    #         ({"BTC": 20, "ETH": 20}),
    #         ({"BTC": 20, "ETH": 20, "ADA": 20}),
    #     ]
    # )
    # def test_set_orders(self, new_orders):
    #     """Checks that set_orders() changes orders attribute"""

    #     self.coinbase.set_orders(**new_orders)
    #     assert self.coinbase.orders == new_orders

    def test_activate(self):
        """Checks that the activate function works accordingly"""

        def after_timeout():
            print("Ending thread...")

        self.coinbase.next_deposit_date = self.todays_date_plus_one_minute
        self.coinbase.next_purchase_date = self.todays_date_plus_one_minute

        for iteration, frequency in enumerate(FREQUENCY_TO_DAYS, 1):

            current_deposit_date = self.coinbase.next_deposit_date
            current_purchase_date = self.coinbase.next_purchase_date

            self.coinbase.update_frequency(frequency)

            orders = {
                "BTC": iteration * 10,
                "BTC": iteration * 20,
                "BTC": iteration * 30,
            }

            self.coinbase.set_orders(**orders)

            # Create thread to do self.coinbase.activate()
            t = Thread(target=self.coinbase.activate)
            t.daemon = True
            t.start()
            Timer(60, after_timeout).start()

            sleep(60)

            assert self.coinbase.next_deposit_date == current_deposit_date + FREQUENCY_TO_DAYS[frequency]
            assert self.coinbase.next_purchase_date == current_purchase_date + FREQUENCY_TO_DAYS[frequency]

            self.coinbase.next_deposit_date += timedelta(minutes=2)
            self.coinbase.next_purchase_date += timedelta(minutes=2)