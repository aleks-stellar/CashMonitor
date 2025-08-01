from unittest.mock import Mock, patch

import pandas as pd
from pytest import CaptureFixture

from src.views import main_views


# Тест основной функции main_views
@patch("src.views.get_dataframe_from_excel")
@patch("src.views.filter_dataframe_by_date")
@patch("src.views.get_time_greeting")
@patch("src.views.calculate_total_spent_and_cashback")
@patch("src.views.get_top_five_transactions")
@patch("src.views.get_user_currency_rates")
@patch("src.views.get_user_stock_rates")
def test_main_views_success(
    mock_get_stocks: Mock,
    mock_get_currencies: Mock,
    mock_get_top: Mock,
    mock_calc_cards: Mock,
    mock_greeting: Mock,
    mock_filter_df: Mock,
    mock_get_df: Mock
) -> None:
    """ Тестирует работы функции main_views с корректными данными. """
    mock_get_df.return_value = "original_df"
    mock_filter_df.return_value = "filtered_df"
    mock_greeting.return_value = "Доброе утро!"
    mock_calc_cards.return_value = pd.DataFrame([{"last_digits": "1234", "total_spent": 1000, "cashback": 50}])
    mock_get_top.return_value = [
        {"date": "01.01.2022", "amount": 100, "category": "Test", "description": "Example"}
    ]
    mock_get_currencies.return_value = [{"currency": "USD", "rate": 93.25}]
    mock_get_stocks.return_value = [{"ticker": "AAPL", "price": 187}]

    result = main_views("2022-01-05 12:00:00")

    assert result == {
        "greeting": "Доброе утро!",
        "cards": [{"last_digits": "1234", "total_spent": 1000, "cashback": 50}],
        "top_transactions": [
            {"date": "01.01.2022", "amount": 100, "category": "Test", "description": "Example"}
        ],
        "currency_rates": [{"currency": "USD", "rate": 93.25}],
        "stock_prices": [{"ticker": "AAPL", "price": 187}]
    }


def test_main_views_invalid_date(capsys: CaptureFixture) -> None:
    """ Тестирует работы функции main_views с некорректной датой. """
    invalid_date = "2022-31-12 12:00:00"
    result = main_views(invalid_date)

    assert result == {}

    captured = capsys.readouterr()
    assert "Проверьте корректность введенной даты." in captured.out
