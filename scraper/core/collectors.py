from .result import CrawlResult


class ListCollector:

    def __init__(self):
        self.results: list[CrawlResult] = []

    def item_scraped(self, item, response, spider):
        self.results.append(
            CrawlResult(
                item=dict(item),
            )
        )

    def spider_error(self, failure, response, spider):
        self.results.append(
            CrawlResult(
                error=failure,
            )
        )