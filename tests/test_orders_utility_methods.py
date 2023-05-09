from datetime import datetime, timedelta

import pytest

from src.orders.utilities import DataInputVerifier


class TestDataInputVerifier:
    current_datetime = datetime.now()
    one_day_ago = (current_datetime + timedelta(days=-1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_hour_ago = (current_datetime - timedelta(hours=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_minute_ago = (current_datetime - timedelta(minutes=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_second_ago = (current_datetime - timedelta(seconds=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_day_later = (current_datetime + timedelta(days=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_hour_later = (current_datetime + timedelta(hours=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_minute_later = (current_datetime + timedelta(minutes=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")
    one_second_later = (current_datetime + timedelta(seconds=1)).strftime("%Y-%m-%d|%I:%M %p").split("|")

    @pytest.mark.parametrize(
        "date_string,expected",
        [
            (1, False),
            ("", False),
            ("Banana", False),
            ("01-01-2022", False),
            ("01/01/2022", False),
            ("2022/01/01", False),
            ("2022-02-29", False),
            ("2022-01-01", True),
            ("2039-06-30", True),
            ("2020-02-29", True),
        ],
    )
    def test_is_valid_date_string(self, date_string, expected):
        """Tests if the given date_string is valid."""

        assert DataInputVerifier.is_valid_date_string(date_string) == expected

    @pytest.mark.parametrize(
        "time_string,expected",
        [
            (1, False),
            ("", False),
            ("Banana", False),
            ("0:00", False),
            ("13:00", False),
            ("13:00 PM", False),
            ("12:61 PM", False),
            ("2:0 PM", False),
            ("1:8 AM", False),
            ("6:32 AM", True),
            ("06:32 AM", True),
            ("12:00 AM", True),
            ("12:00 PM", True),
        ],
    )
    def test_is_valid_time_string(self, time_string, expected):
        """Tests if the given time_string is valid."""

        assert DataInputVerifier.is_valid_time_string(time_string) == expected

    @pytest.mark.parametrize(
        "date_string,time_string,expected",
        [
            ("", "", False),
            ("2039-01-01", "", False),
            ("", "12:00 PM", False),
            ("2039-01-01", "12:00 PM", True),
            ("2032-02-29", "6:42 AM", True),
            ("2020-01-01", "11:37 AM", False),
            (one_day_ago[0], one_day_ago[1], False),
            (one_hour_ago[0], one_hour_ago[1], False),
            (one_minute_ago[0], one_minute_ago[1], False),
            (one_second_ago[0], one_second_ago[1], False),
            (one_day_later[0], one_day_later[1], True),
            (one_hour_later[0], one_hour_later[1], True),
            (one_minute_later[0], one_minute_later[1], False),
            (one_second_later[0], one_second_later[1], False),
        ],
    )
    def test_is_valid_date_and_time_to_start(self, date_string, time_string, expected):
        assert DataInputVerifier.is_valid_date_and_time_to_start(date_string, time_string) == expected

    @pytest.mark.parametrize(
        "frequency,expected",
        [
            ("", False),
            (-1, False),
            ("2021-01-01", False),
            ("10:00 AM", False),
            ("biannually", False),
            ("annually", False),
            ("daily", True),
            ("weekly", True),
            ("biweekly", True),
            ("monthly", True),
        ],
    )
    def test_is_valid_frequency(self, frequency, expected):
        """Tests if the input is a valid frequency."""

        assert DataInputVerifier.is_valid_frequency(frequency) == expected

    @pytest.mark.parametrize(
        "crypto,expected",
        [
            (-1, False),
            ("2021-01-01", False),
            ("10:00 AM", False),
            ("?!?", False),
            ("123", False),
            ("AAPL", False),
            ("BTC", True),
            ("ETH", True),
            ("ADA", True),
        ],
    )
    def test_is_valid_crypto(self, crypto, expected):
        """Tests if the input is a valid crypto."""

        assert DataInputVerifier.is_valid_crypto(crypto) == expected

    @pytest.mark.parametrize(
        "amount,expected",
        [
            ("BTC", False),
            (1, False),
            ("$10", False),
            ("?!?", False),
            ("123abc", False),
            ("-1", False),
            ("0", False),
            ("1", True),
            ("5.00", True),
            ("999999.99", True),
        ],
    )
    def test_is_valid_dollar_amount(self, amount, expected):
        """Tests if the input is a valid dollar amount."""

        assert DataInputVerifier.is_valid_dollar_amount(amount) == expected
