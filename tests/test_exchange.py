from pathlib import Path
from unittest.mock import AsyncMock, call

import pytest
from scrapy.http import HtmlResponse, Request

from scraper.scraper.spiders.exchange import ExchangeSpider


def test_init():
    spider = ExchangeSpider(from_coin="btc", to_coin="eth")

    assert spider.from_coin == "btc"
    assert spider.to_coin == "eth"
    assert len(spider.start_urls) == 1
    assert spider.start_urls[0] == "https://coinmarketcap.com/converter/"


@pytest.mark.parametrize(
    "from_coin, to_coin",
    [
        (None, "btc"),
        ("btc", None),
        (False, "btc"),
        ("btc", 123),
    ],
)
def test_init_type_error(from_coin, to_coin):
    with pytest.raises(TypeError):
        ExchangeSpider(from_coin=from_coin, to_coin=to_coin)


@pytest.mark.parametrize(
    "from_coin, to_coin",
    [
        ("", "btc"),
        ("btc", ""),
        ("   ", "eth"),
        ("eth", "   "),
    ],
)
def test_init_value_error(from_coin, to_coin):
    with pytest.raises(ValueError):
        ExchangeSpider(from_coin=from_coin, to_coin=to_coin)


@pytest.mark.asyncio
async def test_start():
    spider = ExchangeSpider(from_coin="btc", to_coin="eth")

    request = await anext(spider.start())

    assert request.url == "https://coinmarketcap.com/converter/"
    assert request.callback == spider.parse
    assert request.meta["playwright"] is True
    assert request.meta["playwright_include_page"] is True
    assert request.meta["playwright_page_goto_kwargs"] == {"wait_until": "networkidle"}


def make_page_response(mocker):
    html = Path("data/exchange.html").read_text(encoding="utf-8")

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

    return html, page, response


@pytest.mark.asyncio
async def test_parse(mocker):
    _, page, response = make_page_response(mocker)

    number_input = mocker.Mock()
    number_input.wait_for = AsyncMock()
    number_input.fill = AsyncMock()

    from_input = mocker.Mock()
    from_input.wait_for = AsyncMock()
    from_input.fill = AsyncMock()

    from_no_options = mocker.Mock()
    from_no_options.is_visible = AsyncMock(return_value=False)

    from_option = mocker.Mock()
    from_option.wait_for = AsyncMock()
    from_option.click = AsyncMock()
    from_option.nth.return_value = from_option

    to_input = mocker.Mock()
    to_input.wait_for = AsyncMock()
    to_input.fill = AsyncMock()

    to_no_options = mocker.Mock()
    to_no_options.is_visible = AsyncMock(return_value=False)

    to_option = mocker.Mock()
    to_option.wait_for = AsyncMock()
    to_option.click = AsyncMock()
    to_option.nth.return_value = to_option

    result = mocker.Mock()
    result.wait_for = AsyncMock()
    result.nth.return_value = result

    page.locator.side_effect = [
        number_input,
        from_input,
        from_no_options,
        from_option,
        to_input,
        to_no_options,
        to_option,
        result,
    ]

    spider = ExchangeSpider(from_coin="BTC", to_coin="USD")

    items = [item async for item in spider.parse(response)]

    assert len(items) == 1
    assert items[0]["from_coin"]["amount"] == "1"
    assert items[0]["from_coin"]["name"] == "Bitcoin (BTC)"
    assert items[0]["to_coin"]["amount"] == "63,999.90"
    assert items[0]["to_coin"]["name"] == 'United States Dollar "$" (USD)'

    assert page.locator.call_args_list == [
        call('div.cmc-body-wrapper input[type="number"]'),
        call("#react-select-cmc-select__from-input"),
        call("div.cmc-select__menu-notice--no-options"),
        call("div.cmc-body-wrapper div.cmc-select__group div.cmc-select__option"),
        call("#react-select-cmc-select__to-input"),
        call("div.cmc-select__menu-notice--no-options"),
        call("div.cmc-body-wrapper div.cmc-select__group div.cmc-select__option"),
        call("em.cmc-converter__conversion-result"),
    ]

    number_input.wait_for.assert_awaited_once()
    number_input.fill.assert_awaited_once_with("1")

    from_input.wait_for.assert_awaited_once()
    from_input.fill.assert_awaited_once_with("BTC")

    from_no_options.is_visible.assert_awaited_once()

    from_option.wait_for.assert_awaited_once()
    from_option.nth.assert_called_once_with(0)
    from_option.click.assert_awaited_once()

    to_input.wait_for.assert_awaited_once()
    to_input.fill.assert_awaited_once_with("USD")

    to_no_options.is_visible.assert_awaited_once()

    to_option.wait_for.assert_awaited_once()
    from_option.nth.assert_called_once_with(0)
    to_option.click.assert_awaited_once()

    result.wait_for.assert_awaited_once()

    page.content.assert_awaited_once()
    page.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_from_coin_not_found(mocker):
    _, page, response = make_page_response(mocker)

    idle = mocker.Mock()
    idle.wait_for = AsyncMock()
    idle.fill = AsyncMock()
    idle.click = AsyncMock()
    idle.nth.return_value = idle

    from_no_options = mocker.Mock()
    from_no_options.is_visible = AsyncMock(return_value=True)

    page.locator.side_effect = [
        idle,
        idle,
        from_no_options,
    ]

    spider = ExchangeSpider(from_coin="BTC", to_coin="USD")

    with pytest.raises(ValueError, match="Coin 'BTC' not found."):
        async for _ in spider.parse(response):
            pass

    page.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_to_coin_not_found(mocker):
    _, page, response = make_page_response(mocker)

    idle = mocker.Mock()
    idle.wait_for = AsyncMock()
    idle.fill = AsyncMock()
    idle.click = AsyncMock()
    idle.nth.return_value = idle

    from_no_options = mocker.Mock()
    from_no_options.is_visible = AsyncMock(return_value=False)

    to_no_options = mocker.Mock()
    to_no_options.is_visible = AsyncMock(return_value=True)

    page.locator.side_effect = [
        idle,
        idle,
        from_no_options,
        idle,
        idle,
        to_no_options,
    ]

    spider = ExchangeSpider(from_coin="BTC", to_coin="USD")

    with pytest.raises(ValueError, match="Coin 'USD' not found."):
        async for _ in spider.parse(response):
            pass

    page.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_from_coin_parse_error(mocker):
    html, page, response = make_page_response(mocker)

    page.content = AsyncMock(
        return_value=html.replace(
            '<div class="cmc-converter__text">1<!-- --> Bitcoin (BTC)</div>',
            "",
        )
    )

    idle = mocker.Mock()
    idle.wait_for = AsyncMock()
    idle.fill = AsyncMock()
    idle.click = AsyncMock()
    idle.nth.return_value = idle

    no_options = mocker.Mock()
    no_options.is_visible = AsyncMock(return_value=False)

    result = mocker.Mock()
    result.wait_for = AsyncMock()
    result.nth.return_value = result

    page.locator.side_effect = [
        idle,
        idle,
        no_options,
        idle,
        idle,
        no_options,
        idle,
        result,
    ]

    spider = ExchangeSpider(from_coin="BTC", to_coin="USD")

    with pytest.raises(
        ValueError,
        match="Failed to parse from_coin for 'BTC'.",
    ):
        async for _ in spider.parse(response):
            pass

    page.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_parse_to_coin_parse_error(mocker):
    html, page, response = make_page_response(mocker)

    page.content = AsyncMock(
        return_value=html.replace(
            '<em class="cmc-converter__conversion-result">63,999.90</em>',
            "",
        )
    )

    idle = mocker.Mock()
    idle.wait_for = AsyncMock()
    idle.fill = AsyncMock()
    idle.click = AsyncMock()
    idle.nth.return_value = idle

    no_options = mocker.Mock()
    no_options.is_visible = AsyncMock(return_value=False)

    result = mocker.Mock()
    result.wait_for = AsyncMock()
    result.nth.return_value = result

    page.locator.side_effect = [
        idle,
        idle,
        no_options,
        idle,
        idle,
        no_options,
        idle,
        result,
    ]

    spider = ExchangeSpider(from_coin="BTC", to_coin="USD")

    with pytest.raises(
        ValueError,
        match="Failed to parse to_coin for 'USD'.",
    ):
        async for _ in spider.parse(response):
            pass

    page.close.assert_awaited_once()
