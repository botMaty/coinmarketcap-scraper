import scrapy
from scrapy_playwright.page import PageMethod
from scraper.utils.script import scrolling_script


class AllCoinsSpider(scrapy.Spider):
    name = "all_coins"
    allowed_domains = ["coinmarketcap.com"]



    def __init__(self, to_page=81, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.to_page = max(1, int(to_page))
        self.start_urls = [
            f"https://coinmarketcap.com/?page={x}"
            for x in range(1, self.to_page + 1)
        ]

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("evaluate", scrolling_script),
                    PageMethod("wait_for_load_state", "networkidle"),
                ],
            })

    async def parse(self, response):
        page = response.meta["playwright_page"]

        html = await page.content()

        response = response.replace(body=html)

        for cursor in response.css('table.cmc-table tbody:nth-of-type(1) tr'):
            yield {
                "Name": cursor.css("p.coin-item-name::text, a span:nth-child(2)::text").get(),
                "Symbol": cursor.css("p.coin-item-symbol::text, span.crypto-symbol::text").get(),
                "web_path": cursor.css("a::attr(href)").get(),
            }
        
        await page.close()
