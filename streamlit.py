import streamlit as st

from scraper.core.runner import ScraperRunner
from scraper.utils.all_coins_inf import get_all_coins_sym

from scraper.scraper.spiders.search_for_coin import SearchForCoinSpider
from scraper.scraper.spiders.top_10_price import Top10PriceSpider
from scraper.scraper.spiders.top_10_pchange import Top10PChangeSpider
from scraper.scraper.spiders.exchange import ExchangeSpider


if "runner" not in st.session_state:
    st.session_state.runner = ScraperRunner()

if "coins_sym" not in st.session_state:
    st.session_state.coins_sym = tuple(get_all_coins_sym())


st.title("CoinMarketCap Scraping")
st.header("Streamlit Mode")
st.divider()


search_for_coin_tab, top_10_price_tab, top_10_pchange_tab, exchange_tab = st.tabs([
    "Search For Coin",
    "Top-10 By Price",
    "Top-10 By Price Change",
    "Exchange"
])

with search_for_coin_tab:
    symbol = st.selectbox(
        label="Coin symbol",
        options=st.session_state.coins_sym,
        index=None,
        placeholder="e.g., BTC",
    )
    search_for_coin_btn = st.button("Submit", key="btn1")

with top_10_price_tab:
    top_10_price_btn = st.button("Submit", key="btn2")

with top_10_pchange_tab:
    tdomain = st.radio(
        "Time range",
        ("1h", "24h", "7d"),
        horizontal=True,
    )
    top_10_pchange_btn = st.button("Submit", key="btn3")

with exchange_tab:
    col1, col2 = st.columns(2)
    with col1:
        from_coin =  st.text_input("From coin")
    with col2:
        to_coin =  st.text_input("To coin")
    exchange_btn = st.button("Submit", key="btn4")


if search_for_coin_btn:
    pass

if top_10_price_btn:
    pass

if top_10_pchange_btn:
    pass

if exchange_btn:
    pass