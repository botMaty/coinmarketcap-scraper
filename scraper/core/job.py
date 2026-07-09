from threading import Event

from twisted.internet import reactor


class CrawlJob:

    def __init__(self):
        self._done = Event()

        self.results = []
        self.exception = None
        self.reason = None

        self.crawler = None

    def wait(self, timeout=None):
        return self._done.wait(timeout)

    def done(self):
        return self._done.is_set()

    def successful(self):
        return (
            self.done()
            and self.exception is None
            and self.reason == "finished"
        )

    def cancelled(self):
        return self.reason == "cancelled"

    def cancel(self):
        if self.done() or self.crawler is None:
            return False

        reactor.callFromThread(
            self.crawler.engine.close_spider,
            self.crawler.spider,
            reason="cancelled",
        )

        return True

    def result(self, timeout=None):

        if not self.wait(timeout):
            raise TimeoutError("Crawler did not finish.")

        if self.exception is not None:
            raise self.exception

        return self.results