from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from scrapy.http import HtmlResponse, Request

from scraper.scraper.spiders.all_coins import AllCoinsSpider


def test_init():
    spider = AllCoinsSpider(to_page=3)

    assert spider.to_page == 3
    assert len(spider.start_urls) == 3
    assert spider.start_urls[0] == "https://coinmarketcap.com/?page=1"
    assert spider.start_urls[-1] == "https://coinmarketcap.com/?page=3"


@pytest.mark.parametrize("page", [0, -1, "abc", None])
def test_init_raise(page):
    with pytest.raises(ValueError):
        AllCoinsSpider(to_page=page)


@pytest.mark.asyncio
async def test_start():
    spider = AllCoinsSpider(to_page=1)

    request = await anext(spider.start())

    assert request.url == "https://coinmarketcap.com/?page=1"
    assert request.callback == spider.parse
    assert request.meta["playwright"] is True
    assert request.meta["playwright_include_page"] is True
    assert "playwright_page_methods" in request.meta
    assert len(request.meta["playwright_page_methods"]) == 2


@pytest.mark.asyncio
async def test_parse(mocker):

    html = Path("data/all_coins.html").read_text(encoding="utf-8")

    page = mocker.Mock()
    page.content = AsyncMock(return_value=html)
    page.close = AsyncMock()

    request = Request("https://example.com")

    response = HtmlResponse(
        url=request.url,
        request=request,
        body=b"",
    )

    response.meta["playwright_page"] = page

    spider = AllCoinsSpider()

    items = [item async for item in spider.parse(response)]

    assert len(items) == 101

    assert items[0]["Name"] == "CoinMarketCap 20 Index DTF"
    assert items[0]["Symbol"] == "CMC20"
    assert items[0]["web_path"] == "/currencies/coinmarketcap-20-index/"

    assert items[1]["Name"] == "Bitcoin"
    assert items[1]["Symbol"] == "BTC"
    assert items[1]["web_path"] == "/currencies/bitcoin/"

    page.content.assert_awaited_once()
    page.close.assert_awaited_once()
