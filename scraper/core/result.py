class CrawlResult:
    def __init__(self, item=None, error=None):
        self.item = item
        self.error = error

    def __repr__(self):
        res = ""
        if self.item is not None:
            res += str(self.item)
        if self.error is not None:
            res += "\n" + str(self.error)
        return res