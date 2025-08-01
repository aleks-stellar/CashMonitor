import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Union

import pandas as pd
import requests
from dotenv import load_dotenv
from pandas import DataFrame

from config.paths import PATH_TO_LOG_DIR, PATH_TO_LOG_FILE, PATH_TO_USER_SETTINGS
from config.settings import URL_CURRENCY, URL_STOCK

os.makedirs(PATH_TO_LOG_DIR, exist_ok=True)

df_logger = logging.getLogger("app.get_dataframe")
df_logger.setLevel(logging.INFO)
df_handler = logging.FileHandler(PATH_TO_LOG_FILE, mode="w", encoding="utf-8")
df_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
df_handler.setFormatter(df_formatter)
df_logger.addHandler(df_handler)

currency_api_logger = logging.getLogger("app.get_currency_rate")
currency_api_logger.setLevel(logging.INFO)
currency_api_handler = logging.FileHandler(PATH_TO_LOG_FILE, mode="w", encoding="utf-8")
currency_api_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
currency_api_handler.setFormatter(currency_api_formatter)
currency_api_logger.addHandler(currency_api_handler)

stock_api_logger = logging.getLogger("app.get_stock_rate")
stock_api_logger.setLevel(logging.INFO)
stock_api_handler = logging.FileHandler(PATH_TO_LOG_FILE, mode="w", encoding="utf-8")
stock_api_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s: %(message)s")
stock_api_handler.setFormatter(stock_api_formatter)
stock_api_logger.addHandler(stock_api_handler)


# Функции для модуля views
def get_dataframe_from_excel(path_to_excel: Path) -> DataFrame | dict[None, None]:
    """
    Читает EXCEL-файл и конвертирует его в DataFrame.
    :param path_to_excel: Путь к EXCEL-файлу.
    :return: DataFrame с данными о транзакциях.
    """
    df_logger.info(f"The function {get_dataframe_from_excel.__name__} has started...")
    try:
        df_logger.info("Attempt to read excel file...")
        result = pd.read_excel(path_to_excel)
        df_logger.info(f"The function {get_dataframe_from_excel.__name__} has completed correct...")
        return result
    except FileNotFoundError as e:
        df_logger.error("File not found...")
        print(f"Ошибка: {str(e)}")
        df_logger.info(f"The function {get_dataframe_from_excel.__name__} has completed with error...")
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


def get_time_greeting() -> str:
    """
    Возвращает приветствие согласно текущему времени.
    :return: Приветствие.
    """
    time_now = datetime.now().time()

    breakfast = datetime.strptime("06:00:00", "%H:%M:%S").time()
    lunch = datetime.strptime("12:00:00", "%H:%M:%S").time()
    dinner = datetime.strptime("18:00:00", "%H:%M:%S").time()

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
    spend_cashback_sum_cyrillic["Сумма платежа"] = spend_cashback_sum_cyrillic["Сумма платежа"].abs()
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
        operation_date_str = string["Дата операции"].strftime("%d.%m.%Y")
        result_latin.append(
            {
                "date": operation_date_str,
                "amount": abs(string["Сумма платежа"]),
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
    currency_api_logger.info(f"The function {get_user_currency_rate_by_url.__name__} has started...")
    try:
        currency_api_logger.info("Loading environment...")
        load_dotenv()
        apikey = os.getenv("API_KEY_CURRENCY")
        if not apikey:
            currency_api_logger.error("API_KEY_CURRENCY not found in .env file")
            raise ValueError("API_KEY_CURRENCY не найден в .env файле")

        url_currency = URL_CURRENCY

        params: dict = {
            "from": currency_from,
            "to": currency_to,
            "amount": currency_from_amount
        }
        headers = {"apikey": apikey}

        currency_api_logger.info("Sending request...")
        response = requests.get(url=url_currency, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if "result" not in data:
            currency_api_logger.error("Incorrect API response format: no 'result' key")
            raise ValueError("Некорректный формат ответа API: нет ключа 'result'")

        currency_api_logger.info(f"The function {get_user_currency_rate_by_url.__name__} has completed correct...")
        return float(round(data["result"], 2))

    except (requests.RequestException, requests.HTTPError, ValueError) as e:
        print(f"[Ошибка] Не удалось получить курс валюты: {e}")
        currency_api_logger.info(
            f"The function {get_user_currency_rate_by_url.__name__} has completed with error..."
        )
        return None


def get_user_currency_rates() -> list[dict[str, Union[str, float, None]]]:
    """
    Получает курс валют пользователя.
    :return: Список словарей (ключ "currency" - код валюты, значение "rate" - курс валюты к рублю).
    """
    with open(PATH_TO_USER_SETTINGS, encoding="utf-8") as file:
        user_currencies = json.load(file)["user_currencies"]

    result = []
    for currency in user_currencies:
        rate = get_user_currency_rate_by_url(currency_from=currency)
        result.append({"currency": currency, "rate": rate})

    return result


def get_user_stock_rate_by_url(
        stock_ticker: str,
) -> Union[float, None]:
    """
    Получает актуальный курс акции по API.
    :param stock_ticker: Тикер акции.
    :return: Текущий курс акции stock_ticker.
    """
    stock_api_logger.info(f"The function {get_user_stock_rate_by_url.__name__} has started...")
    try:
        load_dotenv()
        api_key = os.getenv("API_KEY_STOCKS")
        if not api_key:
            stock_api_logger.error("API_KEY_CURRENCY not found in .env file")
            raise ValueError("API_KEY_STOCKS не найден в .env файле")

        params: dict = {
            "access_key": api_key,
            "symbols": stock_ticker,
            "limit": 1
        }

        stock_api_logger.info("Sending request...")
        response = requests.get(url=URL_STOCK, params=params)
        response.raise_for_status()
        data = response.json()

        if "data" not in data or not data["data"]:
            stock_api_logger.error("Incorrect API response format: no 'data' key")
            raise ValueError("Некорректный формат ответа API: нет данных")

        close_price = data["data"][0].get("close")
        if close_price is None:
            stock_api_logger.error("Incorrect API response format: no 'close' key in 'data'")
            raise ValueError("Нет цены закрытия (close) в ответе API")

        close_price_rub = get_user_currency_rate_by_url(
            currency_from="USD",
            currency_from_amount=close_price
        )
        if close_price_rub is None:
            stock_api_logger.info(
                f"The function {get_user_stock_rate_by_url.__name__} has completed with error..."
            )
            return None
        else:
            stock_api_logger.info(
                f"The function {get_user_stock_rate_by_url.__name__} has completed correct..."
            )
            return float(round(close_price_rub, 2))

    except (requests.RequestException, requests.HTTPError, ValueError) as e:
        print(f"[Ошибка] Не удалось получить курс акции: {e}")
        stock_api_logger.info(
            f"The function {get_user_stock_rate_by_url.__name__} has completed with error..."
        )
        return None


def get_user_stock_rates() -> list[dict]:
    """
    Получает текущий курс акций пользователя из S&P500.
    :return: Список словарей (ключ "stock" - тикер, значение "price" - курс акции в рублях).
    """
    try:
        with open(PATH_TO_USER_SETTINGS, encoding="utf-8") as file:
            data = json.load(file)
            if "user_stocks" not in data:
                raise ValueError("Некорректный формат файла <user_settings.json>")
            user_stocks = data["user_stocks"]

        stock_prices = []

        for ticker in user_stocks:
            price = get_user_stock_rate_by_url(ticker)
            stock_prices.append({"stock": ticker, "price": price})

        return stock_prices

    except FileNotFoundError as e:
        print(f"[Ошибка] {e}.")
        return []

    except ValueError as e:
        print(f"[Ошибка] {e}.")
        return []
