import scrapy
from scrapy_playwright.page import PageMethod

from scraper.utils.script import scrolling_script


class AllCoinsSpider(scrapy.Spider):
    """Spider that scrap all coins inforamion."""

    name = "all_coins"
    allowed_domains = ["coinmarketcap.com"]

    def __init__(self, to_page=81, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.to_page = int(to_page)
        except (TypeError, ValueError):
            raise ValueError("to_page must be an integer")

        if self.to_page < 1:
            raise ValueError("to_page must be greater than 0")

        self.start_urls = [
            f"https://coinmarketcap.com/?page={x}" for x in range(1, self.to_page + 1)
        ]

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("evaluate", scrolling_script),
                        PageMethod("wait_for_load_state", "networkidle"),
                    ],
                },
                callback=self.parse,
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        try:
            html = await page.content()

            response = response.replace(
                body=html.encode("utf-8"),
                encoding="utf-8",
            )

            for cursor in response.css("table.cmc-table tbody:nth-of-type(1) tr"):
                yield {
                    "Name": cursor.css(
                        "p.coin-item-name::text, a span:nth-child(2)::text"
                    )
                    .get(default="")
                    .strip(),
                    "Symbol": cursor.css(
                        "p.coin-item-symbol::text, span.crypto-symbol::text"
                    )
                    .get(default="")
                    .strip(),
                    "web_path": cursor.css("a::attr(href)").get(default="").strip(),
                }

        finally:
            await page.close()
