from datetime import datetime

from config.paths import PATH_TO_EXCEL_FILE
from src.utils import (calculate_total_spent_and_cashback, filter_dataframe_by_date, get_dataframe_from_excel,
                       get_time_greeting, get_top_five_transactions, get_user_currency_rates, get_user_stock_rates)


def main_views(date_and_time: str) -> dict:
    """
    Предоставляет пользователю основную информацию о транзакциях в формате JSON, совершенных за указанный период.
    Формат JSON-данных, возвращаемых функцией, строго определен и основывается на работе функций модуля utils.
    :param date_and_time: Конечная дата и время отчета о транзакциях (от начала месяца до момента date_and_time)
    в формате YYYY-MM-DD HH:MM:SS.
    :return: JSON-данные за указанный период.
    """
    try:
        user_date_and_time_obj = datetime.strptime(date_and_time, "%Y-%m-%d %H:%M:%S")
        date_and_time_str = datetime.strftime(user_date_and_time_obj, format="%d.%m.%Y %H:%M:%S")

        data_frame = get_dataframe_from_excel(path_to_excel=PATH_TO_EXCEL_FILE)

        filtered_dataframe = filter_dataframe_by_date(data_frame=data_frame, date_and_time=date_and_time_str)

        greeting = get_time_greeting()

        cards_dataframe = calculate_total_spent_and_cashback(dt_frame=filtered_dataframe)
        cards_json = cards_dataframe.to_dict(orient="records")

        top_transactions = get_top_five_transactions(dt_frame=filtered_dataframe)

        currency_rates = get_user_currency_rates()
        stock_prices = get_user_stock_rates()

        result = {
            "greeting": greeting,
            "cards": cards_json,
            "top_transactions": top_transactions,
            "currency_rates": currency_rates,
            "stock_prices": stock_prices
        }

        return result

    except ValueError as e:
        print(f"[Ошибка] {e}. Проверьте корректность введенной даты.")
        return {}
