# Reactor و معماری ScraperRunner

## چرا فقط یک Reactor وجود دارد؟

Reactor قلب Twisted است. همان‌طور که در `asyncio` فقط یک Event Loop
داریم، در Twisted نیز معمولاً فقط **یک Reactor در هر Process** وجود دارد.

وقتی می‌نویسیم:

``` python
from twisted.internet import reactor
```

شیء جدیدی ساخته نمی‌شود؛ بلکه Twisted همان Reactor سراسری (Singleton) را
برمی‌گرداند.

------------------------------------------------------------------------

## چرا Reactor به صورت Singleton طراحی شده است؟

Reactor مسئول مدیریت تمام عملیات غیرهمزمان است:

-   Socketها
-   Connectionها
-   Timerها
-   Callbackها
-   Deferredها
-   Eventهای شبکه

اگر چند Reactor در یک Process وجود داشته باشد، مشخص نیست هر Connection
متعلق به کدام Event Loop باشد؛ بنابراین Twisted فقط یک Reactor را مجاز
می‌داند.

------------------------------------------------------------------------

## ارتباط Runner با Reactor

فرض کنید:

``` python
runner1 = ScraperRunner()
runner2 = ScraperRunner()
```

هر دو Runner در نهایت به همان Reactor مشترک متصل هستند:

``` text
Runner1
    │
    ▼
CrawlerRunner
    │
    ▼
Reactor (مشترک)
    ▲
    │
CrawlerRunner
    │
Runner2
```

------------------------------------------------------------------------

## چرا نباید چند ScraperRunner ساخت؟

در سازنده Runner، Thread مربوط به Reactor ایجاد و `reactor.run()` اجرا
می‌شود.

Runner اول:

``` text
Thread A
    ↓
reactor.run()
```

Runner دوم نیز دوباره سعی می‌کند همان Reactor را اجرا کند که باعث خطا یا
رفتار نامشخص می‌شود.

بنابراین در هر Process فقط **یک ScraperRunner** داشته باشید.

------------------------------------------------------------------------

## آیا می‌توان چند Spider همزمان اجرا کرد؟

بله؛ اتفاقاً Reactor دقیقاً برای همین طراحی شده است.

``` text
                Reactor

                  │

      ┌───────────┼───────────┐

      ▼           ▼           ▼

   Spider1     Spider2     Spider3
```

همه Spiderها داخل همان Event Loop اجرا می‌شوند و Thread جدیدی ساخته
نمی‌شود.

------------------------------------------------------------------------

## نقش ScraperRunner

Runner فقط یک واسط برای ارسال کار به Reactor است.

``` text
Runner

submit(A)
submit(B)
submit(C)

        │
        ▼

     Reactor Queue

        │
        ▼

Spider A
Spider B
Spider C
```

هر بار `submit()` فقط یک Spider جدید را وارد صف اجرای Reactor می‌کند.

------------------------------------------------------------------------

## اگر واقعاً چند Runner بخواهیم چه؟

تنها راه استاندارد، اجرای هر Runner در یک Process جداگانه است:

``` text
Process 1
    Reactor
    Runner

-------------------

Process 2
    Reactor
    Runner
```

هر Process حافظه و Reactor مستقل خودش را دارد.

------------------------------------------------------------------------

## مدیریت Thread و حافظه

در معماری فعلی:

-   فقط یک Thread برای Reactor ساخته می‌شود.
-   برای هر Spider Thread جدید ساخته نمی‌شود.
-   بعد از پایان Crawl، اشیایی مانند Collector و CrawlJob (در صورت
    نداشتن Reference) توسط Garbage Collector آزاد می‌شوند.
-   بنابراین با اجرای تعداد زیادی Crawl، تعداد Threadها افزایش پیدا
    نمی‌کند.

------------------------------------------------------------------------

## خاموش کردن تمیز برنامه

در پایان برنامه بهتر است Reactor نیز متوقف شود:

``` python
def shutdown(self):
    reactor.callFromThread(reactor.stop)
    self._reactor_thread.join()
```

و در فایل اصلی:

``` python
runner = ScraperRunner()

try:
    main(runner)
finally:
    runner.shutdown()
```

این کار باعث آزاد شدن کامل منابع و بسته شدن Thread مربوط به Reactor
می‌شود.

------------------------------------------------------------------------

## جمع‌بندی

در یک Process:

-   ✅ فقط یک Reactor
-   ✅ فقط یک Thread برای Reactor
-   ✅ فقط یک ScraperRunner
-   ✅ هر تعداد Spider به صورت همزمان

در چند Process:

-   ✅ هر Process می‌تواند Reactor و Runner مستقل خودش را داشته باشد.

این معماری همان چیزی است که برای پروژه‌های واقعی مبتنی بر Scrapy و
Twisted توصیه می‌شود.
