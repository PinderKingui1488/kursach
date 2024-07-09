import json
import logging
from logging import Logger
from typing import Any

import pandas as pd


def liggin() -> Logger:
    """
    Настройка логирования, для дальнейшего использования в других модулях
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        filename="utils_log.txt",
        filemode="w",
    )
    logger = logging.getLogger(__name__)
    return logger


def read_xlsx(file_path: str) -> Any:
    """
    функция чтения файла Excel.
    """
    transactions_df = pd.read_excel(file_path)
    return transactions_df.to_dict("records")


def write_json(file_path: str, data: Any) -> None:
    """Red book"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def read_json(file_path: str) -> Any:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
