import streamlit as st

from scraper.core.runner import ScraperRunner
from scraper.scraper.spiders.exchange import ExchangeSpider
from scraper.scraper.spiders.search_for_coin import SearchForCoinSpider
from scraper.scraper.spiders.top_10_pchange import Top10PChangeSpider
from scraper.scraper.spiders.top_10_price import Top10PriceSpider
from scraper.utils.all_coins_inf import get_all_coins_sym


@st.cache_resource
def runner():
    return ScraperRunner()


def disable(elem_disable: str, a: bool):
    st.session_state[elem_disable] = a


@st.fragment(run_every="1000ms")
def search_for_coin_fragment():
    symbol = st.selectbox(
        "Coin symbol",
        options=st.session_state.coins_sym,
        key="search_symbol",
    )

    if st.button(
        "Start",
        key="search_for_coin_btn",
        disabled=st.session_state.search_for_coin_btn_disabled,
    ):
        try:
            job = runner().submit(
                SearchForCoinSpider,
                symbol=symbol,
            )
        except Exception as e:
            st.session_state.search_for_coin_result = str(e)
        else:
            st.session_state.search_for_coin_job = job

        st.session_state.search_for_coin_btn_disabled = True
        st.rerun(scope="fragment")

    if st.session_state.search_for_coin_result is not None:
        st.write(st.session_state.search_for_coin_result)

    job = st.session_state.search_for_coin_job

    if job is None:
        return

    if job.done():
        try:
            res = job.result()
        except Exception as e:
            st.session_state.search_for_coin_job = None
            st.session_state.search_for_coin_result = str(e)
        else:
            st.session_state.search_for_coin_result = res

        st.session_state.search_for_coin_job = None
        st.session_state.search_for_coin_btn_disabled = False

        st.rerun(scope="fragment")
    else:
        st.info("Running...")


@st.fragment(run_every="1000ms")
def top_10_price_fragment():
    if st.button(
        "Start",
        key="top_10_price_btn",
        disabled=st.session_state.top_10_price_btn_disabled,
    ):
        try:
            job = runner().submit(Top10PriceSpider)
        except Exception as e:
            st.session_state.top_10_price_result = str(e)
        else:
            st.session_state.top_10_price_job = job

        st.session_state.top_10_price_btn_disabled = True
        st.rerun(scope="fragment")

    if st.session_state.top_10_price_result is not None:
        st.write(st.session_state.top_10_price_result)

    job = st.session_state.top_10_price_job
    if job is None:
        return

    if job.done():
        try:
            res = job.result()
        except Exception as e:
            st.session_state.top_10_price_job = None
            st.session_state.top_10_price_result = str(e)
        else:
            st.session_state.top_10_price_result = res

        st.session_state.top_10_price_job = None
        st.session_state.top_10_price_btn_disabled = False

        st.rerun(scope="fragment")
    else:
        st.info("Running...")


@st.fragment(run_every="1000ms")
def top_10_pchange_fragment():
    tdomain = st.radio(
        "Time range",
        ("1h", "24h", "7d"),
        horizontal=True,
    )

    if st.button(
        "Start",
        key="top_10_pchange_btn",
        disabled=st.session_state.top_10_pchange_btn_disabled,
    ):
        try:
            job = runner().submit(
                Top10PChangeSpider,
                tdomain=tdomain,
            )
        except Exception as e:
            st.session_state.top_10_pchange_result = str(e)
        else:
            st.session_state.top_10_pchange_job = job

        st.session_state.top_10_pchange_btn_disabled = True
        st.rerun(scope="fragment")

    if st.session_state.top_10_pchange_result is not None:
        st.write(st.session_state.top_10_pchange_result)

    job = st.session_state.top_10_pchange_job
    if job is None:
        return

    if job.done():
        try:
            res = job.result()
        except Exception as e:
            st.session_state.top_10_pchange_job = None
            st.session_state.top_10_pchange_result = str(e)
        else:
            st.session_state.top_10_pchange_result = res

        st.session_state.top_10_pchange_job = None
        st.session_state.top_10_pchange_btn_disabled = False

        st.rerun(scope="fragment")
    else:
        st.info("Running...")


@st.fragment(run_every="1000ms")
def exchange_fragment():
    col1, col2 = st.columns(2)
    with col1:
        from_coin = st.text_input("From coin")
    with col2:
        to_coin = st.text_input("To coin")

    if st.button(
        "Start",
        key="exchange_btn",
        disabled=st.session_state.exchange_btn_disabled,
    ):
        try:
            job = runner().submit(
                ExchangeSpider,
                from_coin=from_coin,
                to_coin=to_coin,
            )
        except Exception as e:
            st.session_state.exchange_result = str(e)
        else:
            st.session_state.exchange_job = job

        st.session_state.exchange_btn_disabled = True
        st.rerun(scope="fragment")

    if st.session_state.exchange_result is not None:
        st.write(st.session_state.exchange_result)

    job = st.session_state.exchange_job

    if job is None:
        return

    if job.done():
        try:
            res = job.result()
        except Exception as e:
            st.session_state.exchange_job = None
            st.session_state.exchange_result = str(e)
        else:
            st.session_state.exchange_result = res

        st.session_state.exchange_job = None
        st.session_state.exchange_btn_disabled = False

        st.rerun(scope="fragment")
    else:
        st.info("Running...")


if "coins_sym" not in st.session_state:
    st.session_state.coins_sym = tuple(get_all_coins_sym())

if "search_for_coin_btn_disabled" not in st.session_state:
    st.session_state.search_for_coin_btn_disabled = False

if "top_10_price_btn_disabled" not in st.session_state:
    st.session_state.top_10_price_btn_disabled = False

if "top_10_pchange_btn_disabled" not in st.session_state:
    st.session_state.top_10_pchange_btn_disabled = False

if "exchange_btn_disabled" not in st.session_state:
    st.session_state.exchange_btn_disabled = False

if "search_for_coin_job" not in st.session_state:
    st.session_state.search_for_coin_job = None

if "top_10_price_job" not in st.session_state:
    st.session_state.top_10_price_job = None

if "top_10_pchange_job" not in st.session_state:
    st.session_state.top_10_pchange_job = None

if "exchange_job" not in st.session_state:
    st.session_state.exchange_job = None

if "search_for_coin_result" not in st.session_state:
    st.session_state.search_for_coin_result = None

if "top_10_price_result" not in st.session_state:
    st.session_state.top_10_price_result = None

if "top_10_pchange_result" not in st.session_state:
    st.session_state.top_10_pchange_result = None

if "exchange_result" not in st.session_state:
    st.session_state.exchange_result = None


st.title("CoinMarketCap Scraping")
st.header("Streamlit Mode")
st.divider()


search_for_coin_tab, top_10_price_tab, top_10_pchange_tab, exchange_tab = st.tabs(
    ["Search For Coin", "Top-10 By Price", "Top-10 By Price Change", "Exchange"]
)


with search_for_coin_tab:
    search_for_coin_fragment()

with top_10_price_tab:
    top_10_price_fragment()

with top_10_pchange_tab:
    top_10_pchange_fragment()

with exchange_tab:
    exchange_fragment()
