from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from scrapy.http import HtmlResponse, Request

from scraper.scraper.spiders.search_for_coin import SearchForCoinSpider


def test_init():
    spider = SearchForCoinSpider(symbol="btc")

    assert len(spider.start_urls) == 1
    assert spider.start_urls[0] == "https://coinmarketcap.com/currencies/bitcoin/"


def test_init_value_error():
    with pytest.raises(ValueError):
        SearchForCoinSpider(symbol=None, match="symbol is required")

    with pytest.raises(ValueError, match="symbol is required"):
        SearchForCoinSpider(symbol="")


def test_init_lookup_error(mocker):
    mocker.patch(
        "scraper.scraper.spiders.search_for_coin.get_url_by_symbol",
        return_value=None,
    )
    with pytest.raises(LookupError, match="Coin 'hajmajid' not found"):
        SearchForCoinSpider(symbol="hajmajid")


@pytest.mark.asyncio
async def test_start():
    spider = SearchForCoinSpider(symbol="btc")

    request = await anext(spider.start())

    assert request.url == "https://coinmarketcap.com/currencies/bitcoin/"
    assert request.callback == spider.parse
    assert request.meta["playwright"] is True
    assert request.meta["playwright_include_page"] is True


@pytest.mark.asyncio
async def test_parse(mocker):
    html = Path("tests/data/search_for_coin.html").read_text(encoding="utf-8")

    page = mocker.Mock()
    page.content = AsyncMock(return_value=html)
    page.close = AsyncMock()

    locator = mocker.Mock()
    locator.nth.return_value = locator
    locator.wait_for = AsyncMock()

    page.locator.return_value = locator

    request = Request("https://example.com")

    response = HtmlResponse(
        url=request.url,
        request=request,
        body=b"",
    )

    response.meta["playwright_page"] = page

    spider = SearchForCoinSpider(symbol="btc")

    items = [item async for item in spider.parse(response)]

    assert len(items) == 1
    assert items[0]["name"] == "Bitcoin"
    assert items[0]["price"] == "$62,987.39"

    page.locator.assert_called_once_with('span[data-test="text-cdp-price-display"]')

    locator.nth.assert_called_once_with(0)
    locator.wait_for.assert_awaited_once()

    page.content.assert_awaited_once()
    page.close.assert_awaited_once()
