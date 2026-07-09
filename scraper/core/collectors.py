from twisted.internet import reactor


class ListCollector:

    def __init__(self, job):
        self.job = job

    def item_scraped(self, item, response, spider):
        self.job.results.append(
            dict(item)
        )

    def spider_error(self, failure, response, spider):

        if self.job.exception is None:
            self.job.exception = failure.value

        reactor.callFromThread(
            spider.crawler.engine.close_spider,
            spider,
            reason="error",
        )