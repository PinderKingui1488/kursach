import unittest
from typing import Any
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.views import calcul_total_expen, get_greet, get_stoc_cur, proc_card_data, read_xlsx, top_transactions_5


@pytest.mark.parametrize(
    "inp, outp",
    [
        ("2022-04-01 11:20:20", "Добрый день!"),
        ("2022-04-01 06:00:44", "Доброе утро!"),
        ("2022-04-01 18:00:00", "Добрый вечер!"),
        ("2022-04-01 00:04:00", "Доброй ночи!"),
    ],
)
def test_get_greeting(inp: str, outp: str) -> None:
    """Проверяет работу функции get_greeting"""
    assert get_greet(inp) == outp


@patch("requests.get")
def mocked_requests_get(*args: Any) -> Any:
    """Заглушка для запросов к API.

    Возвращает моковый ответ с курсом RUB к USD, если timeout = 15,
    иначе возвращает пустой ответ.
    """

    class MockResponse:
        def __init__(self, json_data: Any, status_code: Any) -> None:
            self.json_data = json_data
            self.status_code = status_code

        def json(self) -> Any:
            return self.json_data

    if args[0].timeout == 15:
        return MockResponse({"rates": {"RUB": 70}}, 200)
    else:
        return MockResponse({}, 404)


class TestFunctions(unittest.TestCase):
    """Тестовый класс для функций из src.views."""

    def setUp(self) -> None:
        """Настройка перед тестом."""
        pass

    @patch("yfinance.Ticker")
    def test_get_stock_currency(self, mock_ticker: Any) -> None:
        """Проверяет работу get_stock_currency."""
        mock_data = Mock()
        mock_data.history.return_value = pd.DataFrame({"High": [100]})
        mock_ticker.return_value = mock_data
        self.assertEqual(get_stoc_cur("AAPL"), 100)

    def test_calculate_total_expenses(self) -> None:
        """Проверяет работу calculate_total_expenses."""
        transactions = [{"transaction_amount": -100}, {"transaction_amount": -200}]
        transaction = [
            {"transaction_amount": -100},
            {"transaction_amount": -200},
            {"transaction_amount": -700},
            {"transaction_amount": -50},
        ]
        self.assertEqual(calcul_total_expen(transactions), 300.0)
        self.assertEqual(calcul_total_expen(transaction), 1050.0)

    def test_read_transactions_xlsx(self) -> None:
        """Проверяет работу read_transactions_xlsx."""
        with patch("pandas.read_excel", return_value=pd.DataFrame({})):
            self.assertEqual(read_xlsx("non_existent_file.xls"), [])

    def test_empty_operations(self) -> None:
        """Проверяет работу process_card_data с пустым списком операций."""
        operations: list = []
        self.assertEqual(proc_card_data(operations), [])

    def test_single_card_transaction(self) -> None:
        """Проверяет работу process_card_data с одной транзакцией по одной карте."""
        operations = [
            {"card_number": "*1234567890123456", "transaction_amount": -100.0, "bonuses_including_cashback": 5.0}
        ]
        expected_result = [{"last_digits": "3456", "total_spent": 100.0, "cashback": 5.0}]
        self.assertEqual(proc_card_data(operations), expected_result)

    def test_top_transactions(self) -> None:
        """Проверяет работу top_transactions_5."""
        transactions = [
            {
                "date": "2022-01-01",
                "transaction_amount": -100,
                "category": "Category A",
                "description": "Description A",
            },
            {
                "date": "2022-01-02",
                "transaction_amount": -200,
                "category": "Category B",
                "description": "Description B",
            },
        ]
        expected_result = [
            {
                "category": "Category A",
                "date": "2022-01-01",
                "description": "Description A",
                "transaction_amount": -100,
            },
            {
                "category": "Category B",
                "date": "2022-01-02",
                "description": "Description B",
                "transaction_amount": -200,
            },
        ]
        self.assertEqual(top_transactions_5(transactions), expected_result)


def test_process_card_data() -> None:
    operations = [
        {"card_number": "*1234", "transaction_amount": -100, "bonuses_including_cashback": 50},
        {"card_number": "*5678", "transaction_amount": -50},
        {"card_number": "*1234", "transaction_amount": -200},
        {"card_number": "*9012", "transaction_amount": -75},
    ]
    expected_result = [
        {"cashback": 50.0, "last_digits": "1234", "total_spent": 300.0},
        {"cashback": 0.0, "last_digits": "5678", "total_spent": 50.0},
        {"cashback": 0.0, "last_digits": "9012", "total_spent": 75.0},
    ]
    assert proc_card_data(operations) == expected_result


if __name__ == "__main__":
    unittest.main()
