# Core

The `core/` package provides a lightweight wrapper around Scrapy's `CrawlerRunner`.

Its purpose is to expose a simple and synchronous-looking API while internally using Scrapy and Twisted asynchronously.

The application never interacts with Scrapy directly. Instead, all crawl requests are submitted through `ScraperRunner`.

---

# Components

## ScraperRunner

`ScraperRunner` is the entry point of the framework.

### Responsibilities

- Owns a single `CrawlerRunner`
- Starts the Twisted Reactor
- Submits spiders
- Creates a `CrawlJob` for each crawl
- Schedules crawling safely on the Reactor thread
- Stops the Reactor during application shutdown

### Example

```python
runner = ScraperRunner()

job = runner.submit(
    SearchForCoinSpider,
    symbol="BTC",
)

job.wait()

print(job.result())
```

---

## CrawlJob

Each submitted spider returns a `CrawlJob`.

A `CrawlJob` represents one crawling task and contains everything related to that execution.

### Stored information

- Collected results
- Crawl exception
- Finish reason
- Crawler instance
- Completion state

---

### wait()

```python
job.wait(timeout=None)
```

Blocks the current thread until the crawl finishes.

Returns:

- `True` if the crawl completed before the timeout.
- `False` if the timeout expired.

If `timeout` is omitted, it waits indefinitely.

---

### done()

```python
job.done()
```

Returns:

- `True` if the crawl has already finished.
- `False` while the spider is still running.

This method never blocks.

---

### successful()

```python
job.successful()
```

Returns `True` when:

- the crawl has finished
- no exception occurred

Equivalent to:

```python
job.done() and job.exception is None
```

---

### cancel()

```python
job.cancel()
```

Requests Scrapy to stop the running spider.

Internally this calls:

```python
crawler.engine.close_spider(...)
```

If the spider has already finished, this method has no effect.

The crawl will eventually complete and `wait()` will return.

---

### result()

```python
job.result()
```

Waits for the crawl to finish and returns the collected items.

If an exception occurred before or during crawler execution, the stored exception is raised.

Example:

```python
results = job.result()

for item in results:
    print(item)
```

`result()` follows the same behavior as `concurrent.futures.Future.result()`:

- waits for completion
- raises stored exceptions
- returns successful results

---

## Results and Exceptions

Crawl results are stored directly inside `CrawlJob.results`.

Example:

```python
job.results
```

contains:

```python
[
    {
        "title": "Example",
        "price": 100,
    },
    {
        "title": "Another Item",
        "price": 200,
    }
]
```

Errors are stored separately:

```python
job.exception
```

Example:

```python
if job.exception:
    print(job.exception)
```

A failed crawl does **not** add error objects into `results`.

The separation is intentional:

- `results` contains successful scraped data
- `exception` contains execution failures

---

## ListCollector

The collector receives Scrapy signals and stores results inside the associated `CrawlJob`.

### Responsibilities

- Collect scraped items
- Report spider errors

The collector never starts, stops, or controls spiders.

It only transfers Scrapy events into the corresponding `CrawlJob`.

Scraped items are appended directly:

```python
job.results.append(item)
```

Spider failures are stored:

```python
job.exception = error
```

---

## Signals

`signals.py` connects Scrapy signals to the collector.

Current signals:

- `item_scraped`
- `spider_error`
- `spider_closed`

These signals keep the external `CrawlJob` synchronized with Scrapy's internal execution.

---

## Twisted Integration

Scrapy is built on top of Twisted.

Twisted uses one global event loop called the **Reactor**.

The Reactor is started exactly once inside a dedicated background thread.

```text
Main Thread

CLI / GUI / API

        │
        ▼

ScraperRunner.submit()

        │

reactor.callFromThread()

        │
        ▼

Reactor Thread

CrawlerRunner

Spider
```

All Scrapy operations execute on the Reactor thread.

The main thread never communicates with Scrapy directly.

---

## Running Multiple Spiders

The Runner supports any number of concurrent spiders.

```python
btc = runner.submit(SearchForCoinSpider, symbol="BTC")
eth = runner.submit(SearchForCoinSpider, symbol="ETH")
sol = runner.submit(SearchForCoinSpider, symbol="SOL")
```

Each call returns immediately.

All spiders execute concurrently inside the same Reactor.

```text
               Reactor

                  │

      ┌───────────┼───────────┐

      ▼           ▼           ▼

   Spider A    Spider B    Spider C
```

No additional threads are created.

---

## Runner Lifetime

A Python process should create only one `ScraperRunner`.

Although multiple instances can technically be created, they all share the same global Reactor.

Creating multiple runners is therefore unnecessary and not recommended.

If multiple independent runners are required, use multiple operating system processes instead.

---

## Memory Management

Each crawl creates temporary objects such as:

- Spider
- CrawlJob
- Collector

Once a crawl finishes and no references remain, Python's garbage collector releases them automatically.

The Reactor thread remains alive for the lifetime of the application.

Memory usage depends mainly on the number of stored crawl results.

---

## Shutdown

Before the application exits, the Runner should be shut down.

```python
runner = ScraperRunner()

try:
    main()
finally:
    runner.shutdown()
```

Internally this performs:

```python
reactor.callFromThread(reactor.stop)
self._reactor_thread.join()
```

This stops the Reactor and waits for the background thread to terminate cleanly.

---

## Typical Workflow

```python
runner = ScraperRunner()

job = runner.submit(MySpider)

job.wait()

results = job.result()

runner.shutdown()
```

Or simply:

```python
job = runner.submit(MySpider)

print(job.result())
```

because `result()` automatically waits for completion and raises failures.