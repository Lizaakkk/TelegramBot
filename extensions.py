import requests
import json
from typing import Optional, Dict, Any


class APIException(Exception):
    pass


class CurrencyConverter:

    @staticmethod
    def get_price(base: str, quote: str, amount: str) -> float:
        try:
            amount_float = float(amount)
        except ValueError:
            raise APIException(f"Не удалось обработать количество '{amount}'. "
                               "Введите число в правильном формате (например: 100 или 100.50)")

        if amount_float <= 0:
            raise APIException(f"Количество валюты должно быть больше 0. Вы ввели: {amount}")

        try:
            response = requests.get('https://www.cbr-xml-daily.ru/daily_json.js', timeout=10)
        except requests.exceptions.Timeout:
            raise APIException("Таймаут при подключении к серверу ЦБ РФ. "
                               "Пожалуйста, попробуйте позже.")
        except requests.exceptions.RequestException:
            raise APIException("Ошибка подключения к серверу ЦБ РФ. "
                               "Пожалуйста, попробуйте позже.")

        if response.status_code != 200:
            raise APIException("Ошибка при получении данных о курсах валют. "
                               "Пожалуйста, попробуйте позже.")

        data = json.loads(response.text)

        if base == 'RUB':
            rate_base = 1.0
        elif base in data['Valute']:
            valute = data['Valute'][base]
            rate_base = valute['Value'] / valute['Nominal']
        else:
            available_currencies = ', '.join(data['Valute'].keys())
            raise APIException(f"Валюта '{base}' не найдена в данных ЦБ РФ. "
                               f"Доступные валюты: RUB, {available_currencies}")

        if quote == 'RUB':
            rate_quote = 1.0
        elif quote in data['Valute']:
            valute = data['Valute'][quote]
            rate_quote = valute['Value'] / valute['Nominal']
        else:
            available_currencies = ', '.join(data['Valute'].keys())
            raise APIException(f"Валюта '{quote}' не найдена в данных ЦБ РФ. "
                               f"Доступные валюты: RUB, {available_currencies}")

        result = amount_float * (rate_base / rate_quote)

        return round(result, 2)


class CurrencyHandler:

    CURRENCIES = {
        'евро': 'EUR',
        'доллар': 'USD',
        'рубль': 'RUB',
        'юань': 'CNY',
        'фунт': 'GBP',
        'иена': 'JPY',
        'франк': 'CHF'
    }

    @staticmethod
    def parse_message(message: str) -> tuple:

        parts = message.split()

        if len(parts) != 3:
            raise APIException("Неправильный формат сообщения.\n\n"
                               "Правильный формат:\n"
                               "<валюта, цену которой хотим узнать> <валюта, в которой хотим узнать цену> <количество>\n\n"
                               "Например: евро рубль 100\n"
                               "(узнать цену 100 евро в рублях)")

        base_name, quote_name, amount = parts

        base_name = base_name.lower()
        quote_name = quote_name.lower()

        if base_name not in CurrencyHandler.CURRENCIES:
            raise APIException(f"Валюта '{base_name}' не найдена.\n"
                               f"Доступные валюты: {', '.join(CurrencyHandler.CURRENCIES.keys())}")

        if quote_name not in CurrencyHandler.CURRENCIES:
            raise APIException(f"Валюта '{quote_name}' не найдена.\n"
                               f"Доступные валюты: {', '.join(CurrencyHandler.CURRENCIES.keys())}")

        if base_name == quote_name:
            raise APIException("Вы ввели одинаковые валюты. "
                               "Пожалуйста, выберите разные валюты для конвертации.")

        base_code = CurrencyHandler.CURRENCIES[base_name]
        quote_code = CurrencyHandler.CURRENCIES[quote_name]

        return base_code, quote_code, amount

    @staticmethod
    def get_available_currencies() -> str:
        currencies_list = []
        for russian_name, code in CurrencyHandler.CURRENCIES.items():
            currencies_list.append(f"• {russian_name.capitalize()} ({code})")

        return "Доступные валюты:\n" + "\n".join(currencies_list)

    @staticmethod
    def format_result(base_name: str, quote_name: str, amount: str, result: float) -> str:
        base_name_ru = [k for k, v in CurrencyHandler.CURRENCIES.items()
                        if v == base_name][0].capitalize()
        quote_name_ru = [k for k, v in CurrencyHandler.CURRENCIES.items()
                         if v == quote_name][0].capitalize()

        return (f"{amount} {base_name_ru} ({base_name}) = "
                f"{result} {quote_name_ru} ({quote_name})\n")