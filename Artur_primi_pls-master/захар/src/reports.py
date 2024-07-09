import json
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

from src.utils import liggin

logger = liggin()


def read_xlsx(file_path: str) -> pd.DataFrame:
    """
    Чтение операций из XLS-файла.
    """
    logger.info(f"Чтение данных из файла {file_path}")
    try:
        return pd.read_excel(file_path)
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не обнаружен")
        return pd.DataFrame()


def filter_by_category_date(transactions: pd.DataFrame, category: str, start_date: str) -> Any:
    """
    Фильтрация  по категории и дате, выводит уже отфильтрованные транзакции
    """
    end_date = datetime.strptime(start_date, "%d.%m.%Y") + timedelta(days=90)
    filtered_transactions = transactions[
        (transactions["category"] == category)
        & (transactions["data_payment"] >= start_date)
        & (transactions["data_payment"] < end_date.strftime("d.%m.%Y"))
    ]
    return filtered_transactions.to_dict("records")


def main_reports() -> None:
    """
    функция обеденяющея весь модуль reports(ВСЕ ФУНКЦИИ МОДУЛЯ REPORTS)
    """
    operations = read_xlsx("../data/operations_mi.xls")
    category = input("Напишите категорию: ")
    start_date = input("Напешите дату (от каторой надо считать) 3-месячного периода (например 01.01.2001): ")

    filtered_operations = filter_by_category_date(operations, category, start_date)

    with open("reports.json", "w", encoding="utf-8") as f:
        json.dump(filtered_operations, f, indent=4, ensure_ascii=False)

    logger.info("Отфильтрованные операции записаны сюда reports.json")
    print("Отфильтрованные операции записаны сюда reports.json")


if __name__ == "__main__":
    main_reports()
