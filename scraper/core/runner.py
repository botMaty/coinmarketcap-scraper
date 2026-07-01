from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings

from .collectors import ListCollector
from .signals import connect


class ScraperRunner:

    def __init__(self):
        self.runner = CrawlerRunner(get_project_settings())

    def run(self, spider_cls, **kwargs):
        collector = ListCollector()

        crawler = self.runner.create_crawler(spider_cls)

        connect(crawler, collector)

        d = self.runner.crawl(crawler, **kwargs)

        return d, collector.results


class ScraperProcessRunner:

    def __init__(self):
        self.settings = get_project_settings()
        self.process = CrawlerProcess(self.settings)
        self.spider_count = 0

    def add(self, spider_cls, **kwargs):
        collector = ListCollector()

        crawler = self.process.create_crawler(spider_cls)

        connect(crawler, collector)

        self.process.crawl(crawler, **kwargs)

        self.has_spiders += 1

        return collector.results
    
    def start(self):
        if self.has_spiders == 0:
            return

        self.process.start()

        self.process = CrawlerProcess(self.settings)
        self.has_spiders = 0