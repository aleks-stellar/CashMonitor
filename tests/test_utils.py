import json
from unittest.mock import Mock, mock_open, patch

import pandas as pd
import pandas.testing
import pytest
import requests
from pandas import DataFrame

from config.paths import INVALID_PATH_TO_EXCEL_FILE, PATH_TO_EXCEL_FILE
from src.utils import (calculate_total_spent_and_cashback, filter_dataframe_by_date, get_dataframe_from_excel,
                       get_time_greeting, get_top_five_transactions, get_user_currency_rate_by_url,
                       get_user_currency_rates, get_user_stock_rate_by_url, get_user_stock_rates)


# Тесты для функции get_dataframe_from_excel
@patch("pandas.read_excel")
def test_get_dataframe_from_excel_valid(mock_read_excel: Mock, transactions_dataframe: DataFrame) -> None:
    """ Тестирует работу функции get_dataframe_from_excel с корректным путем к файлу. """
    data = transactions_dataframe
    mock_read_excel.return_value = data
    assert get_dataframe_from_excel(PATH_TO_EXCEL_FILE) == data


def test_get_dataframe_from_excel_invalid_path() -> None:
    """ Тестирует работу функции get_dataframe_from_excel с некорректным путем к файлу. """
    assert get_dataframe_from_excel(INVALID_PATH_TO_EXCEL_FILE) == {}


# Тесты для функции filter_dataframe_by_date
def test_filter_dataframe_by_date_valid(
        transactions_dataframe: DataFrame, filtered_by_data_transactions_dataframe: DataFrame
) -> None:
    """ Тестирует работу функции filter_dataframe_by_date с корректной датой. """
    df_data = pd.DataFrame(transactions_dataframe)
    actual_result = filter_dataframe_by_date(
        date_and_time="24.12.2021 00:00:00", data_frame=df_data
    )
    expected_result = pd.DataFrame(filtered_by_data_transactions_dataframe)
    expected_result["Дата операции"] = pd.to_datetime(expected_result["Дата операции"], dayfirst=True)
    pandas.testing.assert_frame_equal(actual_result, expected_result, check_dtype=False)


@pytest.mark.parametrize("date", [
    "30.02.2020 00:00:00",
    "29.02.2021 00:00:00",
    ""
])
def test_filter_dataframe_by_date_invalid_date(
        transactions_dataframe: DataFrame, date: str) -> None:
    """ Тестирует работу функции filter_dataframe_by_date с некорректной датой. """
    df_data = pd.DataFrame(transactions_dataframe)
    actual_result = filter_dataframe_by_date(
        date_and_time=date, data_frame=df_data
    )
    expected_result = pd.DataFrame()
    pandas.testing.assert_frame_equal(actual_result, expected_result, check_dtype=False)


# Тест для get_time_greeting
@pytest.mark.parametrize("hour, minute, second, expected", [
    (6, 0, 0, "Доброе утро"),
    (7, 0, 0, "Доброе утро"),
    (12, 0, 0, "Добрый день"),
    (13, 0, 0, "Добрый день"),
    (18, 0, 0, "Добрый вечер"),
    (19, 0, 0, "Добрый вечер"),
    (19, 0, 0, "Добрый вечер"),
    (0, 0, 0, "Доброй ночи"),
    (1, 0, 0, "Доброй ночи")
])
def test_get_time_greeting(hour: int, minute: int, second: int, expected: str) -> None:
    """ Тестирует работу функции get_time_greeting с различными вариантами текущего времени. """
    assert get_time_greeting(hour, minute, second) == expected


# Тесты для calculate_total_spent_and_cashback
def test_calculate_total_spent_and_cashback_valid(
        transactions_dataframe: DataFrame, dataframe_calculate_spent_and_cashback: DataFrame
) -> None:
    """ Тестирует работу функции calculate_total_spent_and_cashback с корректным DataFrame. """
    df_data = pd.DataFrame(transactions_dataframe)
    expected_df = (
        pd.DataFrame(dataframe_calculate_spent_and_cashback).sort_values(by="last_digits").reset_index(drop=True)
    )
    actual_df = calculate_total_spent_and_cashback(df_data).sort_values(by="last_digits").reset_index(drop=True)
    pandas.testing.assert_frame_equal(actual_df, expected_df, check_dtype=False)


def test_calculate_total_spent_and_cashback_empty(
        transactions_dataframe_empty: DataFrame, dataframe_calculate_spent_and_cashback_empty: DataFrame
) -> None:
    """ Тестирует работу функции calculate_total_spent_and_cashback с пустым DataFrame. """
    df_data = pd.DataFrame(transactions_dataframe_empty)
    expected_df = pd.DataFrame(dataframe_calculate_spent_and_cashback_empty)
    actual_df = calculate_total_spent_and_cashback(df_data)
    pandas.testing.assert_frame_equal(actual_df, expected_df, check_dtype=False)


# Тесты для get_top_five_transactions
def test_get_top_five_transactions_valid(
        transactions_dataframe: DataFrame, transactions_top_five: list[dict]
) -> None:
    """ Тестирует работу функции get_top_five_transactions с корректными параметрами. """
    df_data = pd.DataFrame(transactions_dataframe)
    actual_result = get_top_five_transactions(df_data)
    expected_result = transactions_top_five
    assert actual_result == expected_result


def test_get_top_five_transactions_empty() -> None:
    """ Тестирует работу функции get_top_five_transactions с пустым DataFrame. """
    df_data = pd.DataFrame({"Дата операции": [], "Сумма платежа": [], "Категория": [], "Описание": []})
    actual_result = get_top_five_transactions(df_data)
    expected_result: list = []
    assert actual_result == expected_result


# Тесты для get_user_currency_rate_by_url
@patch("requests.get")
def test_get_user_currency_rate_by_url_valid(mock_request: Mock, currency_response_example: dict) -> None:
    """ Тестирует работы функции get_user_currency_rate_by_url с корректными данными. """
    mock_request.return_value.json.return_value = currency_response_example
    expected_result = 1490.0
    actual_result = get_user_currency_rate_by_url(
        currency_from="USD",
        currency_to="RUB",
        currency_from_amount=10
    )
    assert actual_result == expected_result


@patch("os.getenv")
def test_get_user_currency_rate_by_url_without_apikey(mock_getenv: Mock) -> None:
    """ Тестирует работы функции get_user_currency_rate_by_url без API-ключа. """
    mock_getenv.return_value = None
    actual_result = get_user_currency_rate_by_url(
        currency_from="USD",
        currency_to="RUB",
        currency_from_amount=10
    )
    assert actual_result is None


@patch("requests.get")
def test_get_user_currency_rate_by_url_exception(mock_request: Mock) -> None:
    """ Тестирует работы функции get_user_currency_rate_by_url с неопределенной ошибкой RequestException. """
    mock_request.side_effect = requests.RequestException
    expected_result = None
    actual_result = get_user_currency_rate_by_url(
        currency_from="USD",
        currency_to="RUB",
        currency_from_amount=10
    )
    assert actual_result == expected_result


@patch("requests.get")
def test_get_user_currency_rate_by_url_without_key(mock_request: Mock) -> None:
    """ Тестирует работы функции get_user_currency_rate_by_url без необходимого ключа. """
    mock_request.return_value.json.return_value = {"success": True}
    expected_result = None
    actual_result = get_user_currency_rate_by_url(
        currency_from="USD",
        currency_to="RUB",
        currency_from_amount=10
    )
    assert actual_result == expected_result


# Тесты для функции get_user_currency_rates
@patch("src.utils.get_user_currency_rate_by_url")
@patch("builtins.open", new_callable=mock_open, read_data='{"user_currencies": ["USD", "EUR"]}')
def test_get_user_currency_rates(mock_open_file: Mock, mock_get_rate: Mock) -> None:
    """ Тестирует работы функции get_user_currency_rates. """
    mock_get_rate.side_effect = [100.5, 120.75]
    result = get_user_currency_rates()
    assert result == [
        {"currency": "USD", "rate": 100.5},
        {"currency": "EUR", "rate": 120.75}
    ]


# Тесты для функции get_user_stock_rate_by_url
@patch("src.utils.get_user_currency_rate_by_url")
@patch("requests.get")
@patch("os.getenv")
def test_get_user_stock_rate_by_url_valid(
        mock_getenv: Mock,
        mock_request: Mock,
        mock_get_rate: Mock,
        stocks_response_example: dict) -> None:
    """ Тестирует работу функции get_user_stock_rate_by_url с корректными данными. """
    mock_getenv.return_value = True
    mock_request.return_value.json.return_value = stocks_response_example
    mock_get_rate.side_effect = [13299.5]
    result = get_user_stock_rate_by_url("AAPL")
    expected_result = 13299.5
    assert result == expected_result


@patch("os.getenv")
def test_get_user_stock_rate_by_url_without_api_key(
        mock_getenv: Mock) -> None:
    """ Тестирует работу функции get_user_stock_rate_by_url без API-ключа. """
    mock_getenv.return_value = None
    result = get_user_stock_rate_by_url("AAPL")
    assert result is None


@patch("requests.get")
@patch("os.getenv")
def test_get_user_stock_rate_by_url_without_close_key(
        mock_getenv: Mock,
        mock_request: Mock
) -> None:
    """ Тестирует работу функции get_user_stock_rate_by_url с некорректным ответом от сервера. """
    mock_getenv.return_value = True
    mock_request.return_value.json.return_value = {"data": [{"open": 129.8}]}
    result = get_user_stock_rate_by_url("AAPL")
    assert result is None


@patch("requests.get")
@patch("os.getenv")
def test_get_user_stock_rate_by_url_without_data_key(
        mock_getenv: Mock,
        mock_request: Mock
) -> None:
    """ Тестирует работу функции get_user_stock_rate_by_url с некорректным ответом от сервера. """
    mock_getenv.return_value = True
    mock_request.return_value.json.return_value = {"open": 129.8}
    result = get_user_stock_rate_by_url("AAPL")
    assert result is None


@patch("src.utils.get_user_currency_rate_by_url")
@patch("requests.get")
@patch("os.getenv")
def test_get_user_stock_rate_by_url_none_rate(
        mock_getenv: Mock,
        mock_request: Mock,
        mock_get_rate: Mock,
        stocks_response_example: dict) -> None:
    """ Тестирует работу функции get_user_stock_rate_by_url, принимающую курс валюты None. """
    mock_getenv.return_value = True
    mock_request.return_value.json.return_value = stocks_response_example
    mock_get_rate.return_value = None
    result = get_user_stock_rate_by_url("AAPL")
    assert result is None


# Тесты для функции get_user_stock_rates
@patch("src.utils.get_user_stock_rate_by_url")
@patch("pathlib.Path.exists", return_value=True)
def test_get_user_stock_rates_valid(
        mock_path_exists: Mock,
        mock_get_stocks: Mock,
        user_stock_rates: list,
        user_currencies_and_stocks: dict
) -> None:
    """ Тестирует работу функции get_user_stock_rates с корректными данными. """
    json_data = json.dumps(user_currencies_and_stocks)
    with patch("builtins.open", mock_open(read_data=json_data)):
        mock_get_stocks.side_effect = [12000.0, 10000.0, 8000.0, 7000.0, 5000.0]
        result = get_user_stock_rates()
        assert result == user_stock_rates


def test_get_user_stock_rates_missing_key() -> None:
    """ Тестирует работы функции get_user_stock_rates без ключа user_currencies. """
    invalid_data = json.dumps({"user_currencies": ["USD"]})

    with patch("pathlib.Path.exists", return_value=True), \
            patch("builtins.open", mock_open(read_data=invalid_data)):
        result = get_user_stock_rates()
        assert result == []


def test_get_user_stock_rates_file_not_found() -> None:
    """ Тестирует работу функции get_user_stock_rates при отсутствии файла. """
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = get_user_stock_rates()
        assert result == []
