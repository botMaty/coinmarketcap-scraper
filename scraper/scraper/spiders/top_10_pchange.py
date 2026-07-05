import scrapy
from scrapy_playwright.page import PageMethod


tdomain_to_num = {
    "1h": 5,
    "24h":6,
    "7d": 7,
}


class Top10PChangeSpider(scrapy.Spider):
    name = "top_10_pchange"
    allowed_domains = ["coinmarketcap.com"]

    def __init__(self, tdomain, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tdomain_num = tdomain_to_num.get(tdomain, 6)

        self.start_urls =[
            "https://coinmarketcap.com"
        ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    # PageMethod("wait_for_load_state", "networkidle"),
                    PageMethod("click", 'div[aria-orientation="horizontal"] div div:nth-child(2) button'),
                    PageMethod("wait_for_selector", 'div.modal-body-wrapper div[data-role="select-trigger"]'),
                    PageMethod("click", 'div.modal-body-wrapper div[data-role="select-trigger"]'),
                    PageMethod("wait_for_selector", 'div.modal-body-wrapper div[data-role="select-trigger"]'),
                    PageMethod("click", 'div[data-role="pp-item"] div div:nth-child(4)'),
                    PageMethod("click", 'div.modal-body-wrapper + div button:nth-child(2)'),
                    PageMethod("wait_for_selector", 'th.stickyTop'),
                    PageMethod("click", f'th.stickyTop:nth-of-type({self.tdomain_num}) div div'),
                    PageMethod("wait_for_selector", 'th.stickyTop:nth-of-type(4) div div [data-direction="desc"]'),
                    PageMethod("wait_for_timeout", 2000),
                ],
            })

    async def parse(self, response):
        print("before yield")
        page = response.meta["playwright_page"]

        html = await page.content()

        response = response.replace(body=html)

        for cursor in response.css('table.cmc-table tbody:nth-of-type(1) tr')[:10]:
            yield {
                "Name": cursor.css("p.coin-item-name::text, a span:nth-child(2)::text").get(),
                "Symbol": cursor.css("p.coin-item-symbol::text, span.crypto-symbol::text").get(),
                "Price": cursor.css("td:nth-child(4) span::text").get(),
                "Price_Change": cursor.css(f"td:nth-child({self.tdomain_num}) span::text").get()
            }

        await page.close()