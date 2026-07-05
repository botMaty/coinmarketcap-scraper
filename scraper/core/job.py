from threading import Event


class CrawlJob:

    def __init__(self):
        self._done = Event()

        self.results = []
        self.exception = None
        self.reason = None

    def wait(self, timeout=None):
        return self._done.wait(timeout)

    def done(self):
        return self._done.is_set()

    def successful(self):
        return self.done() and self.exception is None

    def result(self):
        self.wait()

        if self.exception:
            raise self.exception.value

        return self.results