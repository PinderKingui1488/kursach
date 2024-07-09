import json
from datetime import datetime
from typing import Optional

import pandas as pd

from src.utils import liggin

logger = liggin()


def get_keyword(search_t: str) -> str:
    """
    Возвращает JSON-ответ с транзакциями, содержащими search_t в описании или категории.
    """
    logger.info(f"Поиск по ключевому слову: {search_t}")
    try:
        file_path = "../data/operations_mi.xls"
        data = pd.read_excel(file_path)
        data["description"] = data["description"].astype(str)
        data["category"] = data["category"].astype(str)
        filtered_data = data[
            data["description"].str.contains(search_t, case=False) | data["category"].str.contains(search_t, case=False)
        ]
        trans_list = filtered_data.to_dict(orient="records")
        if not trans_list:
            trans_list = [{"message": "Слово не найдено ни где"}]
        json_response = json.dumps(trans_list, indent=4, ensure_ascii=False)
        with open("services.json", "w", encoding="utf-8") as f:
            json.dump(trans_list, f, indent=4, ensure_ascii=False)
        logger.info("Результаты поиска записаны в файл services.json")
        return json_response
    except FileNotFoundError:
        logger.error("Файл operations_mi.xls не найден.")
        return json.dumps({"error": "Файл operations_mi.xls не найден."}, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Произошла ошибка: {str(e)}")
        return json.dumps({"error": f"Произошла ошибка: {str(e)}"}, indent=4, ensure_ascii=False)


def get_expen_by_categ(transaction: pd.DataFrame, category: str, report_date: Optional[str] = None) -> str:
    """
    Выдает траты по категории за последние 3 месяца от указанной даты(этого его старт ,
     все что раньше этой даты он не берет.
    """
    report_date_dt = datetime.strptime(report_date, "%Y-%m-%d") if report_date else datetime.now()
    logger.info(
        f"Расчет трат по категории: {category} за период  {report_date_dt - pd.DateOffset(months=3)}--{report_date_dt}"
    )
    transaction["data_payment"] = pd.to_datetime(transaction["data_payment"], format="%d.%m.%Y")
    filtered_transactions = transaction[
        (transaction["category"] == category)
        & (transaction["data_payment"] >= report_date_dt - pd.DateOffset(months=3))
        & (transaction["data_payment"] <= report_date_dt)
    ]
    total_expenses = filtered_transactions["payment_amount"].sum()
    result = json.dumps(
        {"category": category, "total_expenses": total_expenses, "report_date": str(report_date_dt.date())},
        indent=4,
        ensure_ascii=False,
    )
    logger.info(f"Результаты расчета: {result}")
    return result


def main_services() -> None:
    """
    Основная функция модуля, которая обьединяет все в модуле services
    """
    # Пример использования:
    print("Ведите слово для поиска например : обед")
    search_1 = input()
    json_result = get_keyword(search_1)
    print(json_result)

    # Пример использования функции get_expenses_by_category
    transactions_df = pd.read_excel("../data/operations_mi.xls")
    print("Ведите слово для поиска например : обед")
    category_to_check = input()
    print("Ведите дату для поиска например : 2222-33-44")
    report_date_to_check = input()
    json_expenses_result = get_expen_by_categ(transactions_df, category_to_check, report_date_to_check)
    print(json_expenses_result)


if __name__ == "__main__":
    main_services()
