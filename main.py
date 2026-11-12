import asyncio
import platform
from datetime import datetime, timedelta

import aiohttp


def get_dates(days):
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(days)]


async def fetch_rates(session, date):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"

    try:
        async with session.get(url) as response:
            if response.status == 200:      
                return await response.json()
            print(f"Помилка: статус {response.status} для {date}")
            return None
    except aiohttp.ClientConnectorError as er:
            print(f"Помилка з'єднання для {date}: {er}")
            return None


def parse_rates(data, date):
    rates = {}
    for item in data["exchangeRate"]:
        if item["currency"] in ("USD", "EUR"):
            rates[item["currency"]] = {
                "sale": item["saleRate"],
                "purchase": item["purchaseRate"],}
    return {date: rates}


async def get_rates(session, date):
    data = await fetch_rates(session, date)
    if data is None:
        return {date: "Помилка: дані недоступні"}
    else:
        return parse_rates(data, date)


async def main(days):
    async with aiohttp.ClientSession() as session:
        tasks = [get_rates(session, date) for date in get_dates(days)]
        return await asyncio.gather(*tasks)


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    while True:
        try:
            days = int(input('Введіть кількість днів (не більше 10): '))
        except ValueError:
            print("Потрібно ввести число")
            continue

        if 1 <= days <= 10:
            break
        print("Число має бути від 1 до 10")

    print(asyncio.run(main(days)))