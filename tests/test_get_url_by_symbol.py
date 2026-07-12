import pytest

from scraper.utils.all_coins_inf import get_url_by_symbol


@pytest.mark.parametrize(
    "sym, url_path",
    [
        ("BTC", "/currencies/bitcoin/"),
        ("btc", "/currencies/bitcoin/"),
        ("bTc", "/currencies/bitcoin/"),
        (" btc ", "/currencies/bitcoin/"),
        (f"{"btc"}", "/currencies/bitcoin/"),
        ("", None),
        ("hajmajid", None),
        (["eth", "btc"][0], "/currencies/ethereum/"),
    ],
)
def test_get_url_by_sym(sym, url_path):
    assert get_url_by_symbol(sym) == url_path


@pytest.mark.parametrize(
    "sym",
    [None, 123, [], {}, 1.5, ["btc"]],
)
def test_get_url_by_symbol_raise(sym):
    with pytest.raises(TypeError, match="sym must be a string"):
        get_url_by_symbol(sym)
