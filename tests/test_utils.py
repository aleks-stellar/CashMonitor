from pathlib import Path
from unittest.mock import Mock, patch
from src.utils import get_dataframe_from_excel

PATH_TO_EXCEL_FILE = Path("..", "data", "operations.xlsx")
INVALID_PATH_TO_EXCEL_FILE = Path("operations.xlsx")


@patch("pandas.read_excel")
def test_get_dataframe_from_excel_valid(mock_read_excel, transactions_dataframe) -> None:
    """Тестирует работу функции get_dataframe_from_excel с корректным путем к файлу"""
    data = transactions_dataframe
    mock_read_excel.return_value = data
    assert get_dataframe_from_excel(PATH_TO_EXCEL_FILE) == data


def test_get_dataframe_from_excel_invalid_path() -> None:
    """Тестирует работу функции get_dataframe_from_excel с некорректным путем к файлу"""
    assert get_dataframe_from_excel(INVALID_PATH_TO_EXCEL_FILE) == {}
