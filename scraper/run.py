from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraper.spiders.exchange import ExchangeSpider
from scraper.spiders.top_10_price import Top10PriceSpider
from scraper.spiders.top_10_pchange import Top10PChangeSpider
from scraper.spiders.search_for_coin import SearchForCoinSpider

process = CrawlerProcess(get_project_settings())

process.crawl(Top10PriceSpider)

process.start()
