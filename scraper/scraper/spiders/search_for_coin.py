import scrapy

from scraper.utils.all_coins_inf import get_url_by_symbol


class SearchForCoinSpider(scrapy.Spider):
    """Spider that scrap coins information by given symbol"""

    name = "search_for_coin"
    allowed_domains = ["coinmarketcap.com"]

    def __init__(self, symbol=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not symbol:
            raise ValueError("symbol is required")

        coin_url = get_url_by_symbol(symbol)

        if coin_url is None:
            raise LookupError(f"Coin '{symbol}' not found")

        self.start_urls = ["https://coinmarketcap.com" + coin_url]

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    # "playwright_page_goto_kwargs": {
                    #     "wait_until": "domcontentloaded",
                    # },
                },
                callback=self.parse,
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        html = await page.content()

        await page.locator('span[data-test="text-cdp-price-display"]').nth(0).wait_for()

        response = response.replace(
            body=html.encode("utf-8"),
            encoding="utf-8",
        )

        yield {
            "Name": response.css('span[data-role="coin-name"]::text')
            .get(default="")
            .strip(),
            "Price": response.css('span[data-test="text-cdp-price-display"]::text')
            .get(default="")
            .strip(),
        }
        await page.close()
