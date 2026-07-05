from scrapy.utils.reactor import install_reactor

install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

import threading

from twisted.internet import reactor

from scrapy.crawler import CrawlerRunner
from scrapy.settings import Settings

from scraper.scraper import settings as project_settings

from .collectors import ListCollector
from .signals import connect
from .job import CrawlJob


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

        crawler = self.runner.create_crawler(spider_cls)

        connect(crawler, collector)

        def _crawl():
            d = self.runner.crawl(crawler, **kwargs)

            def finished(_):
                job._done.set()

            def failed(failure):
                job.exception = failure
                job._done.set()

            d.addCallbacks(finished, failed)

        reactor.callFromThread(_crawl)

        return job
    
    def shutdown(self):
        reactor.callFromThread(reactor.stop)
        self._reactor_thread.join()
