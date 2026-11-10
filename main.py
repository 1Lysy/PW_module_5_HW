import asyncio
import platform
from datetime import datetime, timedelta

import aiohttp


def get_dates(days):
    today = datetime.now()
    return [(today - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(days)]


async def get_rates(session, date):
    url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"
    async with session.get(url) as response:
        data = await response.json()
    rates = {}
    for item in data["exchangeRate"]:
        if item["currency"] in ("USD", "EUR"):
            rates[item["currency"]] = {
                "sale": item["saleRate"],
                "purchase": item["purchaseRate"],
            }
    return {date: rates}


async def main(days):
    if days > 10:
        days = 10

    async with aiohttp.ClientSession() as session:
        tasks = [get_rates(session, date) for date in get_dates(days)]
        return await asyncio.gather(*tasks)


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    print(asyncio.run(main(10)))