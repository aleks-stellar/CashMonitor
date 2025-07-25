from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pandas.testing
import pytest
from pandas import DataFrame

from src.utils import filter_dataframe_by_date, get_dataframe_from_excel

PATH_TO_EXCEL_FILE = Path("..", "data", "operations.xlsx")
INVALID_PATH_TO_EXCEL_FILE = Path("operations.xlsx")


# Тесты для функции get_dataframe_from_excel
@patch("pandas.read_excel")
def test_get_dataframe_from_excel_valid(mock_read_excel: Mock, transactions_dataframe: DataFrame) -> None:
    """Тестирует работу функции get_dataframe_from_excel с корректным путем к файлу"""
    data = transactions_dataframe
    mock_read_excel.return_value = data
    assert get_dataframe_from_excel(PATH_TO_EXCEL_FILE) == data


def test_get_dataframe_from_excel_invalid_path() -> None:
    """Тестирует работу функции get_dataframe_from_excel с некорректным путем к файлу"""
    assert get_dataframe_from_excel(INVALID_PATH_TO_EXCEL_FILE) == {}


# Тесты для функции filter_dataframe_by_date
def test_filter_dataframe_by_date_valid(
        transactions_dataframe: DataFrame, filtered_by_data_transactions_dataframe: DataFrame
) -> None:
    """Тестирует работу функции filter_dataframe_by_date с корректной датой"""
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
    """Тестирует работу функции filter_dataframe_by_date с некорректной датой"""
    df_data = pd.DataFrame(transactions_dataframe)
    actual_result = filter_dataframe_by_date(
        date_and_time=date, data_frame=df_data
    )
    expected_result = pd.DataFrame()
    pandas.testing.assert_frame_equal(actual_result, expected_result, check_dtype=False)
