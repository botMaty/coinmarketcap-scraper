from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

from scraper.spiders.search_for_coin import SearchForCoinSpider
from scraper.spiders.top_10_price import Top10PriceSpider
from scraper.spiders.top_10_pchange import Top10PChangeSpider
from scraper.spiders.exchange import ExchangeSpider

from collectors import ListCollector
from signals import connect


class ScraperRunner:

    def __init__(self):
        self.runner = CrawlerRunner(get_project_settings())

    def run(self, spider_cls, **kwargs):
        collector = ListCollector()

        crawler = self.runner.create_crawler(spider_cls)

        connect(crawler, collector)

        d = self.runner.crawl(crawler, **kwargs)

        return d, collector
