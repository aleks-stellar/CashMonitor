from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pandas.testing
import pytest
from pandas import DataFrame

from src.utils import (calculate_total_spent_and_cashback, filter_dataframe_by_date, get_dataframe_from_excel,
                       get_time_greeting, get_top_five_transactions)

PATH_TO_EXCEL_FILE = Path("..", "data", "operations.xlsx")
INVALID_PATH_TO_EXCEL_FILE = Path("operations.xlsx")


# Тесты для функции get_dataframe_from_excel
@patch("pandas.read_excel")
def test_get_dataframe_from_excel_valid(mock_read_excel: Mock, transactions_dataframe: DataFrame) -> None:
    """ Тестирует работу функции get_dataframe_from_excel с корректным путем к файлу """
    data = transactions_dataframe
    mock_read_excel.return_value = data
    assert get_dataframe_from_excel(PATH_TO_EXCEL_FILE) == data


def test_get_dataframe_from_excel_invalid_path() -> None:
    """ Тестирует работу функции get_dataframe_from_excel с некорректным путем к файлу """
    assert get_dataframe_from_excel(INVALID_PATH_TO_EXCEL_FILE) == {}


# Тесты для функции filter_dataframe_by_date
def test_filter_dataframe_by_date_valid(
        transactions_dataframe: DataFrame, filtered_by_data_transactions_dataframe: DataFrame
) -> None:
    """ Тестирует работу функции filter_dataframe_by_date с корректной датой """
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
    """ Тестирует работу функции filter_dataframe_by_date с некорректной датой """
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
    """ Тестирует работу функции get_time_greeting с различными вариантами текущего времени """
    assert get_time_greeting(hour, minute, second) == expected


# Тесты для calculate_total_spent_and_cashback
def test_calculate_total_spent_and_cashback_valid(
        transactions_dataframe: DataFrame, dataframe_calculate_spent_and_cashback: DataFrame
) -> None:
    """ Тестирует работу функции calculate_total_spent_and_cashback с корректным DataFrame """
    df_data = pd.DataFrame(transactions_dataframe)
    expected_df = (
        pd.DataFrame(dataframe_calculate_spent_and_cashback).sort_values(by="last_digits").reset_index(drop=True)
    )
    actual_df = calculate_total_spent_and_cashback(df_data).sort_values(by="last_digits").reset_index(drop=True)
    pandas.testing.assert_frame_equal(actual_df, expected_df, check_dtype=False)


def test_calculate_total_spent_and_cashback_empty(
        transactions_dataframe_empty: DataFrame, dataframe_calculate_spent_and_cashback_empty: DataFrame
) -> None:
    """ Тестирует работу функции calculate_total_spent_and_cashback с пустым DataFrame """
    df_data = pd.DataFrame(transactions_dataframe_empty)
    expected_df = pd.DataFrame(dataframe_calculate_spent_and_cashback_empty)
    actual_df = calculate_total_spent_and_cashback(df_data)
    pandas.testing.assert_frame_equal(actual_df, expected_df, check_dtype=False)


# Тесты для get_top_five_transactions
def test_get_top_five_transactions_valid(
        transactions_dataframe: DataFrame, transactions_top_five: list[dict]
) -> None:
    """ Тестирует работу функции get_top_five_transactions с корректными параметрами """
    df_data = pd.DataFrame(transactions_dataframe)
    actual_result = get_top_five_transactions(df_data)
    expected_result = transactions_top_five
    assert actual_result == expected_result


def test_get_top_five_transactions_empty() -> None:
    """ Тестирует работу функции get_top_five_transactions с пустым DataFrame """
    df_data = pd.DataFrame({"Дата операции": [], "Сумма платежа": [], "Категория": [], "Описание": []})
    actual_result = get_top_five_transactions(df_data)
    expected_result: list = []
    assert actual_result == expected_result
