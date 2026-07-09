# CoinMarketCap Scraper

## Installation

Clone the repository:

```bash
git clone https://github.com/botMaty/coinmarketcap-scraper.git
cd coinmarketcap-scraper
```

Create and activate a virtual environment:

```bash
python -m venv venv
```

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Project

Run the CLI interface:

```bash
python cli.py
```

Run the Streamlit interface:

```bash
streamlit run streamlit.py
```

## Installing Playwright Browsers

Install a Playwright browser:

```bash
playwright install <browser>
```

Available browser names include:

* `chromium`
* `firefox`
* `webkit`

If you are in Iran, this command may be blocked due to network restrictions. In that case, use a proxy or VPN.

## Scrapy Spiders

### `all_coins`

Extracts all coins from page 1 up to the page number you specify.

> This spider is not available through the CLI or Streamlit interfaces.

### `search_for_coin`

Searches for a coin using its symbol.

It reads the corresponding `url_path` from `data/all_coins.csv` and then extracts the coin's information from CoinMarketCap.

### `top_10_price`

Returns the 10 coins with the highest prices.

### `top_10_pchange`

Returns the 10 coins with the highest positive percentage change.

### `exchange`

Converts one cryptocurrency to another.

## Additional Documentation

### `CORE.md`

Contains usage instructions and explanations for the files inside the `scraper/code/` directory.

### `PLAYWRIGHT_USING_GUIDE.md`

Provides guidelines and best practices for using Playwright inside Scrapy spiders.
