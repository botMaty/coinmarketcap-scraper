import scrapy


class Top10PriceSpider(scrapy.Spider):
    """Spider that scrap top 10 coins which has more price."""

    name = "top_10_price"
    allowed_domains = ["coinmarketcap.com"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        await page.locator("th.stickyTop").nth(3).click()

        await page.wait_for_timeout(2000)

        html = await page.content()

        response = response.replace(
            body=html.encode("utf-8"),
            encoding="utf-8",
        )

        for cursor in response.css("table.cmc-table tbody:nth-of-type(1) tr")[:10]:
            yield {
                "Name": cursor.css("p.coin-item-name::text, a span:nth-child(2)::text")
                .get(default="")
                .strip(),
                "Symbol": cursor.css(
                    "p.coin-item-symbol::text, span.crypto-symbol::text"
                )
                .get(default="")
                .strip(),
                "Price": cursor.css("td:nth-child(4) span::text")
                .get(default="")
                .strip(),
            }

        await page.close()
