import os
from datetime import datetime
from pathlib import Path
from typing import Union

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

from config.settings import URL_CURRENCY


# Функции для модуля views
def get_dataframe_from_excel(path_to_excel: Path) -> DataFrame | dict[None, None]:
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
    Фильтрует транзакции, возвращая операции, совершенные от начала месяца (месяца указанной даты)
    до указанной даты и времени.
    :param data_frame: DataFrame с данными о транзакциях.
    :param date_and_time: Дата и время.
    :return: Отфильтрованный DataFrame.
    """
    try:
        end_date_obj = datetime.strptime(date_and_time, "%d.%m.%Y %H:%M:%S")
        start_date_obj = end_date_obj.replace(day=1, hour=0, minute=0, second=0)
        data_frame["Дата операции"] = pd.to_datetime(
            data_frame["Дата операции"],
            format="%d.%m.%Y %H:%M:%S",
            errors="coerce"
        )
        filtered_data_frame = data_frame[
            (data_frame["Дата операции"] >= start_date_obj) & (data_frame["Дата операции"] <= end_date_obj)
        ]
        return filtered_data_frame.reset_index(drop=True)

    except ValueError as e:
        print(f"Ошибка: {e}. Проверьте корректность введенной даты.")
        return pd.DataFrame()


def get_time_greeting(hour: int = 0, minute: int = 0, second: int = 0) -> str:
    """
    Возвращает приветствие согласно текущему времени.
    :hour: Час для замены.
    :minute: Минута для замены.
    :second: Секунда для замены.
    :return: Приветствие.
    """
    time_now = datetime.now().time()

    # Строка для замены текущего времени при необходимости и для упрощения тестирования
    time_now = time_now.replace(hour=hour, minute=minute, second=second)
    breakfast = datetime.strptime("06:00:00", "%H:%M:%S").time()
    lunch = datetime.strptime("12:00:00", "%H:%M:%S").time()
    dinner = datetime.strptime("18:00:00", "%H:%M:%S").time()

    print(time_now)
    if breakfast <= time_now < lunch:
        return "Доброе утро"
    elif lunch <= time_now < dinner:
        return "Добрый день"
    elif time_now >= dinner:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def calculate_total_spent_and_cashback(dt_frame: DataFrame) -> DataFrame:
    """
    Принимает DataFrame и возвращает DataFrame, в котором посчитаны сумма всех операций
    и суммарный кэшбэк по каждой карте.
    :param dt_frame: DataFrame с данными о транзакциях.
    :return: DataFrame с данными о сумме всех операций и суммарном кэшбэке по картам.
    """
    # Удаляем пустые номера карт
    dt_frame = dt_frame[dt_frame["Номер карты"].str.strip().astype(bool)].copy()

    # Убираем символ * из номеров карт
    dt_frame["Номер карты"] = dt_frame["Номер карты"].str.replace("*", "", regex=False).str.strip()

    # Обработка NaN в кэшбэке
    dt_frame["Кэшбэк"] = pd.to_numeric(dt_frame["Кэшбэк"], errors="coerce").fillna(0)
    dt_frame["Сумма платежа"] = pd.to_numeric(dt_frame["Сумма платежа"], errors="coerce")

    card_number_grouped = dt_frame.groupby("Номер карты")
    spend_cashback_sum_cyrillic = card_number_grouped[["Сумма платежа", "Кэшбэк"]].sum()
    spend_cashback_sum_latin = spend_cashback_sum_cyrillic.rename(columns={
        "Номер карты": "last_digits", "Сумма платежа": "total_spent", "Кэшбэк": "cashback"
    }).rename_axis("last_digits")
    return spend_cashback_sum_latin.reset_index()


def get_top_five_transactions(dt_frame: DataFrame) -> list:
    """
    Составляет список из топ-5 транзакций.
    :param dt_frame: DataFrame с данными о транзакциях.
    :return: Список топ-5 транзакций (каждая транзакция - словарь).
    """
    # Преобразуем столбец в числовой формат
    dt_frame["Сумма платежа"] = pd.to_numeric(dt_frame["Сумма платежа"], errors="coerce")

    # Сортировка происходит по модулю, но значения остаются неизменными
    df_sorted_by_amount = dt_frame.sort_values(
        by="Сумма платежа",
        key=abs,
        kind="stable",
        ascending=False
    ).head(5)

    # Результат - список словарей
    result_cyrillic = df_sorted_by_amount[
        ["Дата операции", "Сумма платежа", "Категория", "Описание"]
    ].to_dict(orient="records")

    # Создаем новый список словарей с другими ключами и изменяем формат даты
    result_latin = []
    for string in result_cyrillic:
        operation_date_obj = datetime.strptime(string["Дата операции"], "%d.%m.%Y %H:%M:%S")
        operation_date_str = datetime.strftime(operation_date_obj, "%d.%m.%Y")
        result_latin.append(
            {
                "date": operation_date_str,
                "amount": string["Сумма платежа"],
                "category": string["Категория"],
                "description": string["Описание"]}
        )

    return result_latin


def get_user_currency_rate_by_url(
        currency_from: str,
        currency_from_amount: int = 1,
        currency_to: str = "RUB"
) -> Union[float, None]:
    """
    Получает актуальный курс валюты по API.
    :param currency_from: Валюта, из которой осуществляется перевод.
    :param currency_from_amount: Сумма в исходной валюте currency_from.
    :param currency_to: Валюта, в которую необходимо перевести.
    :return: Сумма в валюте currency_to.
    """
    try:
        load_dotenv()
        apikey = os.getenv("API_KEY_CURRENCY")
        if not apikey:
            raise ValueError("API_KEY_CURRENCY не найден в .env файле")

        url_currency = URL_CURRENCY

        params: dict = {
            "from": currency_from,
            "to": currency_to,
            "amount": currency_from_amount
        }
        headers = {"apikey": apikey}

        response = requests.get(url=url_currency, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if "result" not in data:
            raise ValueError("Некорректный формат ответа API: нет ключа 'result'")

        return float(data["result"])

    except (requests.RequestException, requests.HTTPError, ValueError) as e:
        print(f"[Ошибка] Не удалось получить курс валюты: {e}")
        return None


# def get_user_currency_rates(path_to_user_settings: Path) -> list[dict]:
#     """
#     Получает курс валют пользователя.
#     :param path_to_user_settings: Путь к JSON-файлу, в котором хранятся коды валют пользователя.
#     :return: Список, в котором каждый словарь дает информацию о текущем курсе валют пользователя.
#     """
#     pass
#
#
# def get_user_stock_rate_by_url(
#         url_for_stock_rate: str,
#         api_for_stock_rate: str,
#         stock_ticker: str,
# ) -> dict:
#     """
#     Получает актуальный курс акции по API.
#     :param url_for_stock_rate: URL для получения актуального курса акции.
#     :param api_for_stock_rate: API для получения актуального курса акции.
#     :param stock_ticker: Тикер акции.
#     :return: Словарь (ключ - тикер, значение - текущая стоимость акции).
#     """
#     pass
#
#
# def get_user_stock_rates(path_to_user_settings: Path) -> list[dict]:
#     """
#     Получает текущий курс акций пользователя из S&P500.
#     :param path_to_user_settings: Путь к JSON-файлу, в котором хранятся тикеры акций пользователя.
#     :return: Список, в котором каждый словарь дает информацию о текущем курсе акций пользователя.
#     """
#     pass
