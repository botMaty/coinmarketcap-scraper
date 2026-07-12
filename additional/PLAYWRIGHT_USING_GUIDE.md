# Scraping Rules

These are the rules I try to follow when building scrapers with Scrapy + Playwright. They're not absolute laws, but they've saved me from a lot of random bugs and broken selectors.

## Rule 1: Keep `playwright_page_methods` simple

Use `playwright_page_methods` only for simple stuff.

Good:

* Open the page
* Maybe wait for a basic load state
* Maybe scroll once

Not so good:

* Clicking through multiple menus
* Filling forms
* Opening modals
* Complex interactions

Once the page starts behaving like an app instead of a document, move everything into `parse()`.

Instead of this:

```python
meta={
    "playwright": True,
    "playwright_page_methods": [
        PageMethod(...),
        PageMethod(...),
        PageMethod(...),
        PageMethod(...),
    ]
}
```

Prefer this:

```python
meta={
    "playwright": True,
    "playwright_include_page": True,
}
```

Then do all interactions inside `parse()`.

It makes debugging much easier.

---

## Rule 2: Wait for the page first

Usually this is enough:

```python
await page.wait_for_load_state("domcontentloaded")
```

Avoid relying on:

```python
await page.wait_for_load_state("networkidle")
```

Many modern websites keep making background requests forever, so `networkidle` can be unreliable.

---

## Rule 3: Every action should use a Locator

Don't do this:

```python
await page.click(selector)
```

Do this:

```python
locator = page.get_by_role("button", name="Filters")

await locator.wait_for()
await locator.click()
```

Locators are much more stable because Playwright automatically re-resolves the element if the page re-renders.

---

## Rule 4: Wait, then click

The pattern should almost always be:

```python
locator = page.get_by_role(...)

await locator.wait_for()
await locator.click()
```

Instead of:

```python
await page.wait_for_selector(...)
await page.click(...)
```

React, Vue, Angular, and friends love rebuilding the DOM. A Locator handles that much better.

---

## Rule 5: Selector priority

Whenever possible, follow this order:

```
id
↓
data-testid
↓
role
↓
label
↓
placeholder
↓
text
↓
css
↓
xpath
```

XPath is the last option, not the first.

---

## Rule 6: Avoid `nth-child()` whenever possible

This:

```css
div:nth-child(2) button
```

works...

...until someone adds another `<div>`.

Instead, try something meaningful:

```python
page.get_by_role("button", name="Filters")
```

or

```python
page.locator("button").filter(has_text="Filters")
```

Selectors should describe *what* you're looking for, not *where* it happens to be today.

---

## Rule 7: Don't fight the DOM

If you find yourself writing something like this:

```xpath
//*[contains(text(),'Filters')]
    /parent::div
    /parent::div
    /parent::button
```

that's usually a sign you're fighting the page.

Try finding the actual button instead.

---

## Rule 8: Avoid random sleeps

This works...

```python
await page.wait_for_timeout(2000)
```

...but only until it doesn't.

Whenever possible, wait for something real.

Examples:

```python
await page.locator("table tbody tr").nth(9).wait_for()
```

or

```python
await page.locator("div.modal-body-wrapper").wait_for()
```

Waiting for actual UI changes is much more reliable than guessing a timeout.

---

## Rule 9: Build helper functions

If you're clicking buttons all over the project, don't repeat yourself.

Example:

```python
async def safe_click(locator):
    await locator.wait_for(state="visible")
    await locator.click()
```

Now your code becomes:

```python
await safe_click(
    page.get_by_role("button", name="Filters")
)
```

Cleaner code.
Less copy-paste.
Much easier to maintain.

---

## Rule 10: Readability beats cleverness

Six simple lines are usually better than one magical selector.

Future you is going to read this code again.

Be nice to future you.

---

## The golden rule

If an interaction involves more than one step, don't squeeze it into `playwright_page_methods`.

Get the `page` object, use Playwright Locators, and write the interaction normally.

It'll be easier to debug, easier to maintain, and much less likely to break when the website changes.
