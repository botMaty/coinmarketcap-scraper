from scrapy import signals

class ListCollector:
    def __init__(self):
        self.items = []

    def item_scraped(self, item, response, spider):
        self.items.append(dict(item))

    def spider_closed(self, spider, reason):
        print("Spider finished")

    def spider_error(self, failure, response, spider):
        print(failure)