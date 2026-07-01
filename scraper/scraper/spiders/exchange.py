import scrapy
from scrapy_playwright.page import PageMethod


class ExchangeSpider(scrapy.Spider):
    name = "exchange"
    allowed_domains = ["coinmarketcap.com"]

    start_urls = [
        "https://coinmarketcap.com/converter/"
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "networkidle"),
                    PageMethod("click", 'div.cmc-body-wrapper input[type="number"]'),
                    PageMethod("fill", 'div.cmc-body-wrapper input[type="number"]', "1"),
                    # PageMethod("click", 'div.cmc-body-wrapper div.cmc-select__value-container'),
                    PageMethod("fill", 'div.cmc-body-wrapper input[id="react-select-cmc-select__from-input"]', "eth"),
                    # PageMethod("wait_for_selector", 'div.cmc-body-wrapper div.cmc-select__group div.cmc-select__option'),
                    PageMethod("click", 'div.cmc-body-wrapper div.cmc-select__group div.cmc-select__option'),
                    # PageMethod("click", 'div.cmc-body-wrapper div.cmc-converter div + div div:nth-child(3) div.cmc-select__value-container'),
                    PageMethod("fill", 'div.cmc-body-wrapper input[id="react-select-cmc-select__to-input"]', "leo"),
                    # PageMethod("wait_for_selector", 'div.cmc-body-wrapper div.cmc-select__group div.cmc-select__option'),
                    PageMethod("click", 'div.cmc-body-wrapper div.cmc-select__group div.cmc-select__option'),
                    PageMethod("wait_for_selector", 'em.cmc-converter__conversion-result'),
                    # PageMethod("wait_for_timeout", 2000),
                ],
            })

    async def parse(self, response):
        page = response.meta["playwright_page"]

        html = await page.content()

        response = response.replace(body=html)

        from_coin = " ".join(t.strip() for t in response.css(
            "div.cmc-converter div.converter__text-row div::text"
            ).getall()[:2] if t.strip())

        yield {
            "FromCoin": from_coin,
            "ToCoin": (response.css("em.cmc-converter__conversion-result::text").get() or "") + (response.css("div.cmc-converter div.converter__text-row div + div + div::text").get() or ""),
            }
        
        await page.close()
