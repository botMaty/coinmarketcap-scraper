from twisted.internet import reactor

from .result import CrawlResult


class ListCollector:

    def __init__(self, job):
        self.job = job

    def item_scraped(self, item, response, spider):
        self.job.results.append(
            CrawlResult(
                item=dict(item),
            )
        )

    def spider_error(self, failure, response, spider):
        self.job.results.append(
            CrawlResult(
                error=failure,
            )
        )

        if self.job.exception is None:
            self.job.exception = failure

        # Fail Fast
        reactor.callFromThread(
            spider.crawler.engine.close_spider,
            spider,
            reason="error",
        )