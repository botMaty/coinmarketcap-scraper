from pathlib import Path
from unittest.mock import AsyncMock, call

import pytest
from scrapy.http import HtmlResponse, Request

from scraper.scraper.spiders.top_10_price import Top10PriceSpider


def test_init():
    spider = Top10PriceSpider()
    assert len(spider.start_urls) == 1
    assert spider.start_urls[0] == "https://coinmarketcap.com"


@pytest.mark.asyncio
async def test_start():
    spider = Top10PriceSpider()

    request = await anext(spider.start())

    assert request.url == "https://coinmarketcap.com"
    assert request.callback == spider.parse
    assert request.meta["playwright"] is True
    assert request.meta["playwright_include_page"] is True
    assert request.meta["playwright_page_goto_kwargs"] == {
        "wait_until": "domcontentloaded"
    }


@pytest.mark.asyncio
async def test_parse(mocker):
    html = Path("data/top_10_price.html").read_text(encoding="utf-8")

    page = mocker.Mock()
    page.content = AsyncMock(return_value=html)
    page.close = AsyncMock()

    filter_button = mocker.Mock()
    filter_button.wait_for = AsyncMock()
    filter_button.click = AsyncMock()

    visible_coin_range_trigger = mocker.Mock()
    visible_coin_range_trigger.wait_for = AsyncMock()
    visible_coin_range_trigger.nth.return_value = visible_coin_range_trigger

    select_trigger = mocker.Mock()
    select_trigger.click = AsyncMock()
    visible_coin_range_trigger.locator.return_value = select_trigger

    show_all_option = mocker.Mock()
    show_all_option.wait_for = AsyncMock()
    show_all_option.nth.return_value = show_all_option
    show_all_option.click = AsyncMock()

    apply_button = mocker.Mock()
    apply_button.click = AsyncMock()

    sort_price = mocker.Mock()
    sort_price.click = AsyncMock()
    sort_price.nth.return_value = sort_price

    page.wait_for_timeout = AsyncMock()

    page.locator.side_effect = [
        visible_coin_range_trigger,
        show_all_option,
        sort_price,
    ]

    page.get_by_role.side_effect = [
        filter_button,
        apply_button,
    ]

    request = Request("https://example.com")

    response = HtmlResponse(
        url=request.url,
        request=request,
        body=b"",
    )

    response.meta["playwright_page"] = page

    spider = Top10PriceSpider()

    items = [item async for item in spider.parse(response)]

    assert len(items) == 10
    assert items[0]["name"] == "Maya Preferred PRA"
    assert items[0]["symbol"] == "MPRA"
    assert items[0]["price"] == "$1,945,287,417.94"
    assert items[1]["name"] == "O Intelligence Coin"
    assert items[1]["symbol"] == "OI"
    assert items[1]["price"] == "$4,602,679.93"

    assert page.locator.call_args_list == [
        call("div.form-item"),
        call('div[data-role="pp-item"] > div > div'),
        call("th.stickyTop"),
    ]

    assert page.get_by_role.call_args_list == [
        call("button", name="Filters"),
        call("button", name="Apply"),
    ]

    filter_button.wait_for.assert_awaited_once()
    filter_button.click.assert_awaited_once()

    visible_coin_range_trigger.wait_for.assert_awaited_once()
    visible_coin_range_trigger.nth.assert_called_once_with(0)
    visible_coin_range_trigger.locator.assert_called_once_with(
        'div[data-role="select-trigger"]'
    )
    select_trigger.click.assert_awaited_once()

    show_all_option.wait_for.assert_awaited_once()
    show_all_option.nth.assert_called_once_with(3)
    show_all_option.click.assert_awaited_once()

    apply_button.click.assert_awaited_once()

    sort_price.nth.assert_called_once_with(3)
    sort_price.click.assert_awaited_once()

    page.wait_for_timeout.assert_awaited_once_with(2000)

    page.content.assert_awaited_once()
    page.close.assert_awaited_once()
