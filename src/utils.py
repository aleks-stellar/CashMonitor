import json
from pathlib import Path
import pandas as pd
from pandas import DataFrame
from datetime import datetime


def get_dataframe_from_excel(path_to_excel: Path) -> DataFrame | None:
    """
    Читает EXCEL-файл и конвертирует его в DataFrame.
    :param path_to_excel: Путь к EXCEL-файлу.
    :return: DataFrame с данными о транзакциях.
    """
    try:
        result = pd.read_excel(path_to_excel)
        return result
    except FileNotFoundError as e:
        print(f"Ошибка: {str(e)}")
        return {}


def filter_dataframe_by_date(data_frame: DataFrame, date_and_time: str) -> DataFrame:
    """
    Фильтрует транзакции, возвращая операции, совершенные от начала месяца до указанной даты и времени.
    :param data_frame: DataFrame с данными о транзакциях.
    :param date_and_time: Текущая дата и время.
    :return: Отфильтрованный DataFrame.
    """
    pass


def get_time_greeting(current_time: str) -> str:
    """
    Возвращает приветствие согласно текущему времени.
    :param current_time: Текущее время.
    :return: Приветствие.
    """
    pass


def get_last_digits(dt_frame: DataFrame) -> str:
    """
    Извлекает последние 4 цифры карты из DataFrame.
    :param dt_frame: DataFrame с данными о транзакциях.
    :return: Последние 4 цифры карты в формате *XXXX.
    """
    pass


def calculate_total_spend_by_card_number(dt_frame: DataFrame, card_number_last_digits: str) -> float:
    """
    Вычисляет сумму расходов по карте из DataFrame.
    :param dt_frame: DataFrame с данными о транзакциях.
    :param card_number_last_digits: Последние 4 цифры карты в формате *XXXX.
    :return: Сумма расходов по данной карте.
    """
    pass


def calculate_total_cashback(total_spend: float) -> float:
    """
    Рассчитывает суммарный кэшбэк по всем операциям за выбранный период.
    :param total_spend: Сумма расходов по конкретной карте за выбранный период.
    :return: Суммарный кэшбэк по конкретной карте за выбранный период.
    """
    pass


def get_top_five_transactions(dt_frame: DataFrame) -> list[dict]:
    """
    Составляет список из топ-5 транзакций.
    :param dt_frame: DataFrame с данными о транзакциях.
    :return: Список топ-5 транзакций (каждая транзакция - словарь).
    """
    pass


def get_user_currency_rate_by_url(
        url_for_currency_rate: str,
        api_for_currency_rate: str,
        currency_from_amount: str,
        currency_from: str,
        currency_to: str
) -> dict:
    """
    Получает актуальный курс валюты по API.
    :param url_for_currency_rate: URL для получения актуального курса валюты.
    :param api_for_currency_rate: API для получения актуального курса валюты.
    :param currency_from_amount: Сумма в исходной валюте.
    :param currency_from: Валюта, из которой осуществляется перевод.
    :param currency_to: Валюта, в которую необходимо перевести.
    :return: Словарь (ключ - код валюты, значение - результат перевода).
    """
    pass


def get_user_currency_rates(path_to_user_settings: Path) -> list[dict]:
    """
    Получает курс валют пользователя.
    :param path_to_user_settings: Путь к JSON-файлу, в котором хранятся коды валют пользователя.
    :return: Список, в котором каждый словарь дает информацию о текущем курсе валют пользователя.
    """
    pass


def get_user_stock_rate_by_url(
        url_for_stock_rate: str,
        api_for_stock_rate: str,
        stock_ticker: str,
) -> dict:
    """
    Получает актуальный курс акции по API.
    :param url_for_stock_rate: URL для получения актуального курса акции.
    :param api_for_stock_rate: API для получения актуального курса акции.
    :param stock_ticker: Тикер акции.
    :return: Словарь (ключ - тикер, значение - текущая стоимость акции).
    """
    pass


def get_user_stock_rates(path_to_user_settings: Path) -> list[dict]:
    """
    Получает текущий курс акций пользователя из S&P500.
    :param path_to_user_settings: Путь к JSON-файлу, в котором хранятся тикеры акций пользователя.
    :return: Список, в котором каждый словарь дает информацию о текущем курсе акций пользователя.
    """
    pass
