from scrapy import signals


def connect(crawler, collector):

    crawler.signals.connect(
        collector.item_scraped,
        signal=signals.item_scraped,
        weak=False,
    )

    crawler.signals.connect(
        collector.spider_error,
        signal=signals.spider_error,
        weak=False,
    )

    def closed(spider, reason):
        collector.job.reason = reason
        collector.job._done.set()

    crawler.signals.connect(
        closed,
        signal=signals.spider_closed,
        weak=False,
    )