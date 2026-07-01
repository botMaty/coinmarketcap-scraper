import scrapy
from scrapy_playwright.page import PageMethod
from scraper.utils.all_coins_inf import get_url_by_sym


class SearchForCoinSpider(scrapy.Spider):
    name = "search_for_coin"
    allowed_domains = ["coinmarketcap.com"]

    def __init__(self, symbol=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.symbol = symbol
        self.start_urls = [
            "https://coinmarketcap.com" + get_url_by_sym(self.symbol)
        ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    # PageMethod("wait_for_load_state", "networkidle"),
                    PageMethod("wait_for_selector", 'span[data-test="text-cdp-price-display"]'),
                ],
            })

    async def parse(self, response):
        page = response.meta["playwright_page"]

        html = await page.content()

        response = response.replace(body=html)

        
        yield {
            "Name": response.css('span[data-role="coin-name"]::text').get(),
            "Price": response.css('span[data-test="text-cdp-price-display"]::text').get(),
        }
        await page.close()
