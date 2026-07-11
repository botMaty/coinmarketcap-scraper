import scrapy

tdomain_to_num = {
    "1h": 5,
    "24h": 6,
    "7d": 7,
}


class Top10PChangeSpider(scrapy.Spider):
    name = "top_10_pchange"
    allowed_domains = ["coinmarketcap.com"]

    def __init__(self, tdomain, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not tdomain:
            raise ValueError("tdomain is required")

        self.tdomain_num = tdomain_to_num.get(tdomain, None)

        if self.tdomain_num is None:
            raise ValueError(f"Invalid time domain: '{tdomain}'")

        self.start_urls = ["https://coinmarketcap.com"]

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_goto_kwargs": {
                        "wait_until": "domcontentloaded",
                    },
                },
                callback=self.parse,
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        btn = page.get_by_role("button", name="Filters")
        await btn.wait_for()
        await btn.click()

        loc = page.locator("div.form-item").nth(0)
        await loc.wait_for()
        await loc.locator('div[data-role="select-trigger"]').click()

        loc = page.locator('div[data-role="pp-item"] > div > div').nth(3)
        await loc.wait_for()
        await loc.click()

        await page.get_by_role("button", name="Apply").click()

        await page.locator("th.stickyTop").nth(self.tdomain_num - 1).click()

        await page.wait_for_timeout(2000)

        html = await page.content()

        response = response.replace(body=html)

        for cursor in response.css("table.cmc-table tbody:nth-of-type(1) tr")[:10]:
            yield {
                "Name": cursor.css(
                    "p.coin-item-name::text, a span:nth-child(2)::text"
                ).get(),
                "Symbol": cursor.css(
                    "p.coin-item-symbol::text, span.crypto-symbol::text"
                ).get(),
                "Price": cursor.css("td:nth-child(4) span::text").get(),
                "Price_Change": cursor.css(
                    f"td:nth-child({self.tdomain_num}) span::text"
                ).get(),
            }

        await page.close()
