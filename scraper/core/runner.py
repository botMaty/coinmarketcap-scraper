from scrapy.utils.reactor import install_reactor

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

import threading

from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings
from twisted.internet import reactor

from scraper.scraper import settings as project_settings

from .collectors import ListCollector
from .job import CrawlJob
from .signals import connect

settings = Settings()
settings.setmodule(project_settings)


class ScraperRunner:

    def __init__(self):
        self.runner = CrawlerRunner(settings)

        self._reactor_thread = threading.Thread(
            target=reactor.run,
            kwargs={
                "installSignalHandlers": False,
            },
            daemon=True,
        )

        self._reactor_thread.start()

    def submit(self, spider_cls, **kwargs):

        job = CrawlJob()
        collector = ListCollector(job)

        def _crawl():
            try:
                crawler = self.runner.create_crawler(spider_cls)
                job.crawler = crawler

                connect(crawler, collector)

                d = self.runner.crawl(crawler, **kwargs)

            except Exception as e:
                job.exception = e
                job.reason = "error"
                job.crawler = None
                job._done.set()
                return

            def finished(_):
                job.crawler = None
                return _

            def failed(failure):
                if job.exception is None:
                    job.exception = failure.value

                job.reason = "error"
                job.crawler = None

                if not job.done():
                    job._done.set()

                return failure

            d.addCallbacks(finished, failed)

        reactor.callFromThread(_crawl)

        return job

    def shutdown(self):
        reactor.callFromThread(reactor.stop)
        self._reactor_thread.join()