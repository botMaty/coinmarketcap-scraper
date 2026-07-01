from scraper.core.runner import ScraperProcessRunner

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


def search_for_coin():
    pass

def top_10_by_price():
    pass

def top_10_by_price_change():
    pass

def exchange():
    pass

def menu(options):
    while True:
        choice = TerminalMenu(options, title="Select your operation:").show()

        if choice == 0:
            search_for_coin()
        elif choice == 1:
            top_10_by_price()
        elif choice == 2:
            top_10_by_price_change()
        elif choice == 3:
            exchange()
        else:
            break

        TerminalMenu(["Press Enter..."]).show()

def show_banner(banner: str):
    for char in banner:
        print(char, end='', flush=True)
        if char.isalpha():
            time.sleep(0.05)

def main():
    global banner
    global options

    show_banner(banner)
    menu(options)

if __name__ == "__main__":
    main()