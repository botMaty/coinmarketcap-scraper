from scrapy import signals

def connect(crawler, collector):
    crawler.signals.connect(
        collector.item_scraped,
        signal=signals.item_scraped,
    )

    crawler.signals.connect(
        collector.spider_closed,
        signal=signals.spider_closed,
    )

    crawler.signals.connect(
        collector.spider_error,
        signal=signals.spider_error,
    )