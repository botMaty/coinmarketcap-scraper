from scrapy.crawler import CrawlerRunner

runner = CrawlerRunner(settings)

collector = ResultCollector()

crawler = runner.create_crawler(CoinSpider)

crawler.signals.connect(
    collector.item_scraped,
    signal=signals.item_scraped,
)

d = runner.crawl(crawler)