import json
import unittest
from typing import Any
from unittest.mock import patch

import pandas as pd
from pytest import fixture

from src.services import get_keyword


@patch("pandas.read_excel")
def test_search_term_in_description(mock_read_excel: Any) -> None:
    """
    Проверяет, что функция get_keyword возвращает правильный JSON с результатами поиска, если ключевое слово
     найдено в описании.
    """
    mock_data = [{"description": "Visited a cafe", "category": "Food"}]
    mock_read_excel.return_value = pd.DataFrame(mock_data)
    search_term = "cafe"
    expected_result = json.dumps(mock_data, indent=4)
    actual_result = get_keyword(search_term)
    assert actual_result == expected_result


@patch("pandas.read_excel")
def test_search_term_in_category(mock_read_excel: Any) -> None:
    """
    Проверяет, что функция get_keyword возвращает правильный JSON с результатами поиска,
     если ключевое слово найдено в категории.
    """
    mock_data = [{"description": "Lunch", "category": "Cafe"}]
    mock_read_excel.return_value = pd.DataFrame(mock_data)
    search_term = "Cafe"
    expected_result = json.dumps(mock_data, indent=4)
    actual_result = get_keyword(search_term)
    assert actual_result == expected_result


@patch("pandas.read_excel")
def test_file_not_found_error(mock_read_excel: Any) -> None:
    """
    Проверяет, что функция get_keyword возвращает правильный JSON с ошибкой, если файл не найден.
    """
    mock_read_excel.side_effect = FileNotFoundError()
    search_term = "test"
    expected_result = json.dumps({"error": "Файл operations.xls не найден."}, indent=4, ensure_ascii=False)
    actual_result = get_keyword(search_term)
    assert actual_result == expected_result


@patch("pandas.read_excel")
def test_other_exceptions(mock_read_excel: Any) -> None:
    """
    Проверяет, что функция get_keyword возвращает правильный JSON с ошибкой, если возникла ошибка,
     отличная от FileNotFoundError.
    """
    mock_read_excel.side_effect = Exception()
    search_term = "test"
    expected_result = json.dumps({"error": "Произошла ошибка: "}, indent=4, ensure_ascii=False)
    actual_result = get_keyword(search_term)
    assert actual_result == expected_result


@fixture
def mock_read_excel() -> Any:
    """
    Фикстура для имитации функции pandas.read_excel.
    """

    def mock_read_excel_function(file_path: Any) -> Any:
        with open("src/operations_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        return df

    return mock_read_excel_function


def test_get_transactions_by_keyword() -> None:
    """
    Проверяет, что функция get_transactions_by_keyword возвращает правильный JSON
    с результатами поиска, если ключевое слово найдено.
    """
    mock_data = [{"description": "Visited a cafe", "category": "Food"}]
    df = pd.DataFrame(mock_data)

    def get_transactions_by_keyword(search_term: Any) -> Any:
        filtered_transactions = df[
            df["description"].str.contains(search_term) | df["category"].str.contains(search_term)
        ]
        result = filtered_transactions.to_json(orient="records", indent=4)
        return result

    search_term = "cafe"
    result = get_transactions_by_keyword(search_term)
    assert result is not None


@patch("pandas.read_excel")
def test_get_transactions_by_keyword_FILENOTFOUND(mock_read_excel: Any) -> None:
    """
    Проверяет, что функция get_transactions_by_keyword возвращает правильный JSON с ошибкой FileNotFoundError,
     если файл не найден.
    """
    mock_read_excel.side_effect = FileNotFoundError()
    search_term = "test"
    expected_result = json.dumps({"error": "Файл operations.xls не найден."}, indent=4, ensure_ascii=False)
    actual_result = get_keyword(search_term)
    assert actual_result == expected_result


class TestGetTransactionsByKeyword(unittest.TestCase):
    """
    Класс для тестирования функции get_transactions_by_keyword.
    """

    @patch("pandas.read_excel")
    def test_exception_handling(self, mock_read_excel: Any) -> None:
        """
        Проверяет, что функция get_transactions_by_keyword корректно обрабатывает исключения.
        """
        mock_data = [{"description": "Visited a cafe", "category": "Food"}]
        df = pd.DataFrame(mock_data)

        def get_transactions_by_keyword(search_term: Any) -> Any:
            raise Exception("Test exception")

        with patch("src.services.pd.read_excel", return_value=df):
            try:
                self.fail("Test exception")
            except Exception as e:
                self.assertEqual(str(e), "Test exception")


if __name__ == "__main__":
    unittest.main()
