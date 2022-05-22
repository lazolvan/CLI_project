import argparse
import datetime
import json
import requests


def parser() -> tuple:
#Принимает аргументы из командной строки и возвращает список
    parser_args = argparse.ArgumentParser()
    parser_args.add_argument("currency", nargs="?", default=None)
    parser_args.add_argument(
        "date", nargs="?",
        default=datetime.datetime.today().strftime("%Y-%m-%d")
    )
    return parser_args.parse_args().currency, parser_args.parse_args().date


def prints(*args):
    frst_line, second_line = "______________", "=============="
    if len(args) == 1:
        print(frst_line, f"{args[0]}", second_line, sep="\n")
    else:
        print(frst_line, f"{args[0]}", "", f"{args[1]}", second_line, sep="\n")


def date_check(date: str) -> bool:
    """
Проверка входящей строки на корректность указанной даты.
Корректный формат - Г,М,Д. Выдает ошибку, если ввести будущую дату или
раньше 1999года (не поддерживается API)
    """
    try:
        date = datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return False
    else:
        return (date - datetime.datetime.now()).days < 0 and date.year > 1998


def convert_date(date: str) -> str or None:
#Проверяет дату и преобразовывает в необходимый формат для запроса
    if date_check(date):
        return date.replace("-", "")
    else:
        prints(f"Неверная дата {date}")
        return None


def get_req(date: str) -> list[dict]:
#Запрос апи с параметром даты, возвращает данные со всеми доступными валютами
    url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory" \
          f"/exchange?date={date}&json"
    response = requests.request("GET", url)
    if response.status_code != 200 or json.loads(response.text) == []:
        prints("Ошибка!")
        return []
    else:
        return json.loads(response.text)


def get_information():
    currency, raw_date = parser()
    date = convert_date(raw_date)

    if currency and date:
        currency = currency.upper()
        data = get_req(date)
        if data: #находим валюту и ее курс в словарях
            rate = [
                i.get("rate") for i in data if
                i.get("cc") == currency
            ]
            if rate: #если найдена, принтим валюту и курс
                prints(currency, *rate)
            else:
                prints(
                    f"{currency}",
                    f"Валюта на найдена"
                )
    elif not currency: #Если не передать валюту в консоли
        prints("System Error")


if __name__ == '__main__':
    get_information()
