import unittest.mock as mock
from datetime import datetime, timedelta

import pytest

from src.orders.command_line_input_collection import CommandLineInputCollector


class TestInputCollector:
    input_collector = CommandLineInputCollector()
    current_datetime = datetime.now()
    today = current_datetime.strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_day_ago = (current_datetime - timedelta(days=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_minute_later = (current_datetime + timedelta(minutes=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_second_later = (current_datetime + timedelta(seconds=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_day_later = (current_datetime + timedelta(days=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    two_days_ago = (current_datetime - timedelta(days=2)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    thirty_minutes_ago = (current_datetime - timedelta(minutes=2)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    twelve_hours_ago = (current_datetime - timedelta(hours=12)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_month_later = (current_datetime + timedelta(days=32)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_year_later = (current_datetime + timedelta(days=365)).strftime("%Y-%m-%d|%I:%M %p").split("|")

    @pytest.mark.parametrize(
        "list_of_user_inputs,expected",
        [
            (["1", "Banana", "01-01-2025", "1/1/2025", "01/01/25", "2022-02-29", "2025-01-01"], "2025-01-01"),
            (["2024-11-31", "2024-11-30", "1/1/2025", "01/01/25", "2022-02-29"], "2024-11-30"),
            (["2021-02-29", "2025-02-29", "2029-02-29", "2030-02-29", "2032-02-29"], "2032-02-29"),
            (["1/1/01", "1/1/2001", "01/01/21", "2001/01/01", "2001-01-01"], "2001-01-01"),
            (["01-01-2025", "1/1/2025", "01/01/25", "2022-02-29", "2020-09-30"], "2020-09-30"),
        ],
    )
    def test_get_start_date(self, list_of_user_inputs, expected):
        """Tests CommandLineInputCollector.get_start_date()."""

        with mock.patch("builtins.input", side_effect=list_of_user_inputs):
            assert self.input_collector.get_start_date() == expected

    @pytest.mark.parametrize(
        "list_of_user_inputs,expected",
        [
            (["1", "Banana", "2 o'clock noon", "3:61 AM", "13:30 PM", "12:30PM", "12:30 PM"], "12:30 PM"),
            (["3:61 AM", "15:00", "12:30PM", "3:33 AM"], "3:33 AM"),
            (["1:00", "1 PM", "1:0 PM", "1:00PM", "1:00 PM"], "1:00 PM"),
            (["13:59 AM", "12:60PM", "2:01 PM", "12:59 AM"], "2:01 PM"),
            (["3:61 AM", "12:00PM", "12:00AM", "13:30 PM", "12:29PM", "12:29 PM"], "12:29 PM"),
        ],
    )
    def test_get_start_time(self, list_of_user_inputs, expected):
        """Tests CommandLineInputCollector.get_start_time()."""

        with mock.patch("builtins.input", side_effect=list_of_user_inputs):
            assert self.input_collector.get_start_time() == expected

    @pytest.mark.parametrize(
        "list_of_user_inputs,expected",
        [
            (
                [
                    today[0],
                    today[1],
                    one_day_ago[0],
                    one_day_ago[1],
                    one_minute_later[0],
                    one_minute_later[1],
                    one_second_later[0],
                    one_second_later[1],
                    one_day_later[0],
                    one_day_later[1],
                ],
                (one_day_later[0], one_day_later[1]),
            ),
            (
                [
                    thirty_minutes_ago[0],
                    thirty_minutes_ago[1],
                    one_minute_later[0],
                    one_minute_later[1],
                    twelve_hours_ago[0],
                    twelve_hours_ago[1],
                    one_month_later[0],
                    one_month_later[1],
                ],
                (one_month_later[0], one_month_later[1]),
            ),
            (
                [
                    two_days_ago[0],
                    two_days_ago[1],
                    one_day_ago[0],
                    one_day_ago[1],
                    one_year_later[0],
                    one_year_later[1],
                    one_second_later[0],
                    one_second_later[1],
                    one_day_later[0],
                    one_day_later[1],
                ],
                (one_year_later[0], one_year_later[1]),
            ),
        ],
    )
    def test_get_start_datetime(self, list_of_user_inputs, expected):
        """Tests CommandLineInputCollector.get_start_time()."""

        with mock.patch("builtins.input", side_effect=list_of_user_inputs):
            assert self.input_collector.get_start_datetime() == expected

    @pytest.mark.parametrize(
        "list_of_user_inputs,expected",
        [
            (["bimonthly", "biannually", "quarterly", "seasonally", "daily"], "daily"),
            (["yearly", "semiannually", "weekly", "fortnight", "seasonally"], "weekly"),
            (["biweekly", "semiannually", "quarterly", "fortnight", "seasonally"], "biweekly"),
            (["biannually", "semiannually", "monthly", "fortnight", "daily"], "monthly"),
        ],
    )
    def test_get_frequency(self, list_of_user_inputs, expected):
        """Tests CommandLineInputCollector.get_frequency()."""

        with mock.patch("builtins.input", side_effect=list_of_user_inputs):
            assert self.input_collector.get_frequency() == expected

    @pytest.mark.parametrize(
        "list_of_user_inputs,expected",
        [
            (["AAPL", "BTC", "Six hundred dollars", "600", "N"], {"BTC": 600.00}),
            (["FB", "BTC", "0", "600", "Y", "BTC", "N", "N"], {"BTC": 600.00}),
            (["GOOG", "BTC", "0", "600", "Y", "BTC", "Y", "400", "N"], {"BTC": 400.00}),
            (["BTC", "666.66", "Y", "BTC", "N", "Y", "BTC", "Y", "300.00", "N"], {"BTC": 300.00}),
            (["BTC", "666.66", "Y", "BTC", "N", "N", "BTC", "300.00", "400", "N"], {"BTC": 666.66}),
        ],
    )
    def test_get_orders(self, list_of_user_inputs, expected):
        """Tests CommandLineInputCollector.get_orders()."""

        with mock.patch("builtins.input", side_effect=list_of_user_inputs):
            assert self.input_collector.get_orders() == expected
