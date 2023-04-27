from datetime import date, datetime, timedelta

import pytest

from src.coinbase.input_collection import InputCollector


class TestInputCollector:
    input_collector = InputCollector()

    todays_datetime = datetime.today()

    todays_date = todays_datetime.strftime("%Y-%m-%d")
    yesterdays_date = (todays_datetime + timedelta(days=-1)).strftime("%Y-%m-%d")
    tomorrows_date = (todays_datetime + timedelta(days=1)).strftime("%Y-%m-%d")

    last_year = todays_datetime.year - 1
    last_new_year_date = date(last_year, 1, 1).strftime("%Y-%m-%d")

    next_year = todays_datetime.year + 1
    new_year_date = date(next_year, 1, 1).strftime("%Y-%m-%d")

    current_time = todays_datetime.strftime("%I:%M %p")
    current_time_minus_one_minute = (todays_datetime + timedelta(minutes=-1)).strftime("%I:%M %p")
    current_time_plus_one_minute = (todays_datetime + timedelta(minutes=1)).strftime("%I:%M %p")

    @pytest.mark.parametrize(
        "date_string,expected",
        [
            # Invalid Parameters
            ("", False),
            (-1, False),
            ("banana", False),
            (100.00, False),
            ("01-01-2022", False),
            ("01/01/2022", False),
            ("2022-02-30", False),
            # Valid Parameters
            (last_new_year_date, False),
            (yesterdays_date, False),
            (todays_date, True),
            (tomorrows_date, True),
            (new_year_date, True),
        ],
    )
    def test_is_valid_start_date(self, date_string, expected):
        """Tests if the given start date is valid."""

        result = self.input_collector.is_valid_start_date(date_string)
        assert result == expected

    @pytest.mark.parametrize(
        "time_string,expected",
        [
            # Invalid Parameters
            ("", False),
            (-1, False),
            ("banana", False),
            ("19:45pm", False),
            ("10:00am", False),
            # Valid Parameters
            (current_time_minus_one_minute, False),
            (current_time, False),
            (current_time_plus_one_minute, True),
        ],
    )
    def test_is_valid_start_time_if_start_date_is_today(self, time_string, expected):
        """Tests if the input is a valid start time assuming the valid start date is today."""

        self.input_collector.start_date_is_today = True
        result = self.input_collector.is_valid_start_time(time_string)
        assert result == expected

    @pytest.mark.parametrize(
        "time_string,expected",
        [
            # Invalid Parameters
            ("", False),
            (-1, False),
            ("banana", False),
            ("19:45pm", False),
            ("10:00am", False),
            # Valid Parameters
            (current_time_minus_one_minute, True),
            (current_time, True),
            (current_time_plus_one_minute, True),
        ],
    )
    def test_is_valid_start_time_if_start_date_is_not_today(self, time_string, expected):
        """Tests if the input is a valid start time if the valid start date is after today"""

        self.input_collector.start_date_is_today = False
        result = self.input_collector.is_valid_start_time(time_string)
        assert result == expected

    @pytest.mark.parametrize(
        "frequency,expected",
        [
            # Invalid Parameters
            ("", False),
            (-1, False),
            ("2021-01-01", False),
            ("10:00 AM", False),
            ("biannually", False),
            ("annually", False),
            # Valid Parameters
            ("daily", True),
            ("weekly", True),
            ("biweekly", True),
            ("monthly", True),
        ],
    )
    def test_is_valid_frequency(self, frequency, expected):
        """Tests if the input is a valid frequency."""

        result = self.input_collector.is_valid_frequency(frequency)
        assert result == expected

    @pytest.mark.parametrize(
        "crypto,expected",
        [
            # Invalid Parameters
            (-1, False),
            ("2021-01-01", False),
            ("10:00 AM", False),
            ("daily", False),
            ("?!?", False),
            ("123", False),
            # Valid Parameters
            ("BTC", True),
            ("ETH", True),
            ("ADA", True),
            ("SHIB", True),
        ],
    )
    def test_is_valid_crypto(self, crypto, expected):
        """Tests if the input is a valid crypto."""

        result = self.input_collector.is_valid_crypto(crypto)
        assert result == expected

    @pytest.mark.parametrize(
        "amount,expected",
        [
            # Invalid Parameters
            ("BTC", False),
            (-1, False),
            ("2021-01-01", False),
            ("10:00 AM", False),
            ("$10", False),
            (10, False),
            ("?!?", False),
            ("123abc", False),
            ("-1", False),
            # Valid Parameters
            ("0", False),
            ("1", True),
            ("5.00", True),
            ("100", True),
            ("1500.69", True),
        ],
    )
    def test_is_valid_dollar_amount(self, amount, expected):
        """Tests if the input is a valid dollar amount."""

        result = self.input_collector.is_valid_dollar_amount(amount)
        assert result == expected
