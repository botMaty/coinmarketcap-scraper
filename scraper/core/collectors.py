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

        self.job.exception = failure