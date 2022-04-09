import pytest

from coinbase.input_collection import InputCollector


class TestInputCollector():

    input_collector = InputCollector()

    @pytest.mark.parametrize(
        "date_string,expected",
        [
            ("", False),
            (-1, False),
            ("banana", False),
            (100.00, False),
            ("2022-02-30", False),
            ("2021-01-01", False),
            ("01-01-2022", False),
            ("01/01/2022", False),
            ("2022-06-15", True),
            ("2023-01-01", True),
        ]
    )
    def test_is_valid_start_date(self, date_string, expected):
        """Tests if the given start date is valid."""

        result = self.input_collector.is_valid_start_date(date_string)
        assert result == expected

    @pytest.mark.parametrize(
        "time_string,expected",
        [
            ("", False),
            (-1, False),
            ("banana", False),
            ("19:45pm", False),
            ("10:00am", False),
            ("10:00 am", True),
            ("10:00 AM", True),
            ("5:45 PM", True),
            ("05:45 PM", True),
            ("06:30 am", True),
        ]
    )
    def test_is_valid_start_time_if_start_date_is_today(self, time_string, expected):
        """Tests if the input is a valid start time if the start date is today."""

        self.input_collector.start_date_is_today = True
        result = self.input_collector.is_valid_start_time(time_string)
        assert result == expected

    @pytest.mark.parametrize(
        "time_string,expected",
        [
            ("", False),
            (-1, False),
            ("banana", False),
            ("19:45pm", False),
            ("10:00am", False),
            ("10:00 am", True),
            ("10:00 AM", True),
            ("5:45 PM", True),
            ("05:45 PM", True),
            ("06:30 am", True),
        ]
    )
    def test_is_valid_start_time_if_start_date_is_not_today(self, time_string, expected):
        """Tests if the input is a valid start time if the start date is not today."""
                
        self.input_collector.start_date_is_today = False
        result = self.input_collector.is_valid_start_time(time_string)
        assert result == expected

    @pytest.mark.parametrize(
        "frequency,expected",
        [
            ("", False),
            (-1, False),
            ("2021-01-01", False),
            ("10:00 AM", False),
            ("daily", True),
            ("weekly", True),
            ("biweekly", True),
            ("monthly", True),
            ("biannually", False),
            ("annually", False)
        ]
    )
    def test_is_valid_frequency(self, frequency, expected):
        """Tests if the input is a valid frequency."""

        result = self.input_collector.is_valid_frequency(frequency)
        assert result == expected

    @pytest.mark.parametrize(
        "crypto,expected",
        [
            ("BTC", True),
            (-1, False),
            ("2021-01-01", False),
            ("10:00 AM", False),
            ("daily", False),
            ("ETH", True),
            ("ADA", True),
            ("SHIB", True),
            ("?!?", False),
            ("123", False)
        ]
    )
    def test_is_valid_crypto(self, crypto, expected):
        """Tests if the input is a valid frequency."""

        result = self.input_collector.is_valid_crypto(crypto)
        assert result == expected

    @pytest.mark.parametrize(
        "amount,expected",
        [
            ("BTC", False),
            (-1, False),
            ("2021-01-01", False),
            ("10:00 AM", False),
            ("5.00", True),
            ("$10", False),
            ("10", True),
            (10, False),
            ("?!?", False),
            ("123abc", False)
        ]
    )
    def test_is_valid_dollar_amount(self, amount, expected):
        """Tests if the input is a valid dollar amount."""

        result = self.input_collector.is_valid_dollar_amount(amount)
        assert result == expected
        