import scrapy


class ExchangeSpider(scrapy.Spider):
    """Spider that exchange coins."""

    name = "exchange"
    allowed_domains = ["coinmarketcap.com"]

    def __init__(self, from_coin=None, to_coin=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not isinstance(from_coin, str):
            raise TypeError("from_coin must be a string")

        if not isinstance(to_coin, str):
            raise TypeError("to_coin must be a string")

        if not from_coin.strip():
            raise ValueError("from_coin is required")

        if not to_coin.strip():
            raise ValueError("to_coin is required")

        self.from_coin = from_coin
        self.to_coin = to_coin
        self.start_urls = ["https://coinmarketcap.com/converter/"]

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_goto_kwargs": {
                        "wait_until": "networkidle",
                    },
                },
                callback=self.parse,
            )

    async def parse(self, response):
        page = response.meta["playwright_page"]

        inp = page.locator('div.cmc-body-wrapper input[type="number"]')
        await inp.wait_for()
        await inp.fill("1")

        inp = page.locator("#react-select-cmc-select__from-input")
        await inp.wait_for()
        await inp.fill(self.from_coin)

        loc = page.locator(
            "div.cmc-body-wrapper div.cmc-select__group div.cmc-select__option"
        ).nth(0)
        await loc.wait_for()
        await loc.click()

        inp = page.locator("#react-select-cmc-select__to-input")
        await inp.wait_for()
        await inp.fill(self.to_coin)

        loc = page.locator(
            "div.cmc-body-wrapper div.cmc-select__group div.cmc-select__option"
        ).nth(0)
        await loc.wait_for()
        await loc.click()

        await page.locator("em.cmc-converter__conversion-result").nth(0).wait_for()

        html = await page.content()

        response = response.replace(
            body=html.encode("utf-8"),
            encoding="utf-8",
        )

        from_coin_res = " ".join(
            t.strip()
            for t in response.css(
                "div.cmc-converter div.converter__text-row div::text"
            ).getall()[:2]
            if t.strip()
        )

        yield {
            "FromCoin": from_coin_res,
            "ToCoin": (
                response.css("em.cmc-converter__conversion-result::text")
                .get(default="")
                .strip()
            )
            + (
                response.css(
                    "div.cmc-converter div.converter__text-row div + div + div::text"
                )
                .get(default="")
                .strip()
            ),
        }

        await page.close()
