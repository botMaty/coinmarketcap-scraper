from scraper.core.runner import ScraperRunner

from scraper.scraper.spiders.search_for_coin import SearchForCoinSpider
from scraper.scraper.spiders.top_10_price import Top10PriceSpider
from scraper.scraper.spiders.top_10_pchange import Top10PChangeSpider
from scraper.scraper.spiders.exchange import ExchangeSpider

from simple_term_menu import TerminalMenu

import time


banner = """
╔══════════════════════════════╗
║    CoinMarketCap Scraping    ║
║           CLI Mode           ║
╚══════════════════════════════╝

"""

options = [
    "Search For Coin",
    "Top-10 By Price",
    "Top-10 By Price Change",
    "Exchange",
    "Quit"
]


def search_for_coin(runner: ScraperRunner):
    symbol = input("Coin symbol: ")
    try:
        job = runner.submit(
            SearchForCoinSpider,
            symbol=symbol
        )
        print("Running...")
        res = job.result()
    except Exception as e:
        print(e)
    else:
        print(res)

def top_10_by_price(runner: ScraperRunner):
    try:
        job = runner.submit(Top10PriceSpider)
        print("Running...")
        res = job.result()
    except Exception as e:
        print(e)
    else:
        print(res)

def top_10_by_price_change(runner: ScraperRunner):
    tdomain = input("Time range (1h/24h/7d): ")
    try:
        job = runner.submit(
            Top10PChangeSpider,
            tdomain=tdomain,
        )
        print("Running...")
        res = job.result()
    except Exception as e:
        print(e)
    else:
        print(res)

def exchange(runner: ScraperRunner):
    from_coin = input("From Coin: ")
    to_coin = input("To Coin: ")
    try:
        job = runner.submit(
            ExchangeSpider,
            from_coin=from_coin,
            to_coin=to_coin,
        )
        print("Running...")
        res = job.result()
    except Exception as e:
        print(e)
    else:
        print(res)

def menu(options, runner: ScraperRunner):
    while True:
        choice = TerminalMenu(options, title="Select your operation:").show()

        if choice == 0:
            search_for_coin(runner)
        elif choice == 1:
            top_10_by_price(runner)
        elif choice == 2:
            top_10_by_price_change(runner)
        elif choice == 3:
            exchange(runner)
        else:
            break

        # TerminalMenu(["Press Enter..."]).show()
        input("Press Enter...")

def show_banner(banner: str):
    for char in banner:
        print(char, end='', flush=True)
        if char.isalpha():
            time.sleep(0.05)

def main():
    global banner
    global options

    runner = ScraperRunner()

    show_banner(banner)
    menu(options, runner)
    runner.shutdown

if __name__ == "__main__":
    main()