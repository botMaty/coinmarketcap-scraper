import scrapy

class TestSpider(scrapy.Spider):
    name = "test"

    def start_requests(self):
        yield scrapy.Request(
            "https://example.com",
            meta={
                "playwright": True,
                "playwright_include_page": True,
            },
        )

    async def parse(self, response):
        print(response.meta.keys())
        print("page =", response.meta.get("playwright_page"))