from pathlib import Path
from unittest.mock import AsyncMock, call

import pytest
from scrapy.http import HtmlResponse, Request

from scraper.scraper.spiders.top_10_pchange import Top10PChangeSpider


def test_init():
    spider = Top10PChangeSpider(tdomain="1h")

    assert spider.tdomain_num == 5
    assert len(spider.start_urls) == 1
    assert spider.start_urls[0] == "https://coinmarketcap.com"


def test_init_tdomain_missing():
    with pytest.raises(ValueError, match="tdomain is required"):
        Top10PChangeSpider(tdomain=None)
    with pytest.raises(ValueError, match="tdomain is required"):
        Top10PChangeSpider(tdomain="")


def test_init_type_error():
    with pytest.raises(TypeError, match="tdomain must be a string"):
        Top10PChangeSpider(tdomain=1)
    with pytest.raises(TypeError, match="tdomain must be a string"):
        Top10PChangeSpider(tdomain=["1"])


def test_init_tdomain_missing():
    with pytest.raises(ValueError, match="Invalid time domain: '1'"):
        Top10PChangeSpider(tdomain="1")
    with pytest.raises(ValueError, match="Invalid time domain: '7day'"):
        Top10PChangeSpider(tdomain="7day")


@pytest.mark.asyncio
async def test_start():
    spider = Top10PChangeSpider(tdomain="1h")

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
    html = Path("tests/data/top_10_pchange.html").read_text(encoding="utf-8")

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

    sort_pchange = mocker.Mock()
    sort_pchange.click = AsyncMock()
    sort_pchange.nth.return_value = sort_pchange

    page.wait_for_timeout = AsyncMock()

    page.locator.side_effect = [
        visible_coin_range_trigger,
        show_all_option,
        sort_pchange,
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

    spider = Top10PChangeSpider(tdomain="1h")

    items = [item async for item in spider.parse(response)]

    assert len(items) == 10
    assert items[0]["name"] == "Step App"
    assert items[0]["symbol"] == "FITFI"
    assert items[0]["price"] == "$0.0002615"
    assert items[0]["price_change"] == "219.64%"
    assert items[1]["name"] == "RECON"
    assert items[1]["symbol"] == "RECON"
    assert items[1]["price"] == "$0.001009"
    assert items[1]["price_change"] == "147.67%"

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

    sort_pchange.nth.assert_called_once_with(4)
    sort_pchange.click.assert_awaited_once()

    page.wait_for_timeout.assert_awaited_once_with(2000)

    page.content.assert_awaited_once()
    page.close.assert_awaited_once()
