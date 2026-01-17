import telebot
from config import TOKEN
from extensions import CurrencyConverter, CurrencyHandler, APIException


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message: telebot.types.Message):
    help_text = (
        "Конвертер валют\n\n"
        "Для конвертации валюты отправьте сообщение в формате:\n"
        "<имя валюты, цену которой хотим узнать> <имя валюты, в которой хотим узнать цену> <количество>\n\n"
        "Примеры:\n"
        "евро рубль 100 - узнать цену 100 евро в рублях\n"
        "доллар евро 50.5 - узнать цену 50.5 долларов в евро\n"
        "рубль юань 1000 - узнать цену 1000 рублей в юанях\n\n"
        "Доступные команды:\n"
        "/start, /help - показать это сообщение\n"
        "/values - показать доступные валюты\n\n"
        "Внимание: используйте точку для десятичных дробей (например: 100.50)"
    )
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=['values'])
def handle_values(message: telebot.types.Message):
    currencies_info = CurrencyHandler.get_available_currencies()
    bot.send_message(message.chat.id, currencies_info)


@bot.message_handler(content_types=['text'])
def handle_text(message: telebot.types.Message):
    try:
        base, quote, amount = CurrencyHandler.parse_message(message.text)

        result = CurrencyConverter.get_price(base, quote, amount)

        formatted_result = CurrencyHandler.format_result(base, quote, amount, result)

        bot.send_message(message.chat.id, formatted_result)

    except APIException as e:
        bot.send_message(message.chat.id, f"Ошибка: {str(e)}")

    except Exception as e:
        error_msg = f"Произошла непредвиденная ошибка: {str(e)}\n\nПожалуйста, попробуйте еще раз."
        bot.send_message(message.chat.id, error_msg)
        print(f"Произошла ошибка: {e}")


if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)