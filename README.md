> [!IMPORTANT]
> I am not the original author of this package. [I found it on pypi](https://pypi.org/project/playwright-webdriver-py) and noticed its github repo is gone. Since I found it useful and needed to make some fixes, I decided to re-publish it and maintain it myself.

# playwright-webdriver-py

**Run existing Selenium WebDriver Python scripts using Playwright as the browser backend — no ChromeDriver or browser binary installation required.**

`playwright-webdriver-py` is a drop-in compatibility layer that implements the Selenium WebDriver Python API over [Playwright's](https://playwright.dev/) synchronous API. Drop it in and your existing `webdriver.Chrome()` scripts run backed by Playwright; faster, more reliable, and without the ChromeDriver version-matching headache.

---

## Features

- **Zero script changes** — existing Selenium scripts run as-is
- **No ChromeDriver** — Playwright manages its own browser binaries
- **Full `WebDriverWait` / `expected_conditions` support** — unchanged from Selenium
- **Chromium, Firefox, and WebKit** backends via `PlaywrightBrowserType`
- **CLI runner** — execute any `.py` Selenium script directly from the command line
- **`PlaywrightBy`** — opt-in raw Playwright selector strings for power users

---

## Installation

```bash
pip install playwright-webdriver-py
playwright install  # downloads browser binaries (first time only)
```

Or with [Poetry](https://python-poetry.org/):

```bash
poetry add playwright-webdriver-py
playwright install
```

**Requirements:** Python 3.12+

---

## Quick Start

### Run an existing Selenium script unchanged

```python
# my_existing_script.py  — written for standard Selenium, runs on Playwright
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

driver.get("https://www.wikipedia.org")
search = wait.until(EC.presence_of_element_located((By.ID, "searchInput")))
search.send_keys("Playwright (software)")
search.submit()

heading = wait.until(EC.presence_of_element_located((By.ID, "firstHeading")))
print(heading.text)

driver.quit()
```

**Via the CLI runner** (intercepts `webdriver.Chrome()` transparently):

```bash
python -m playwright_webdriver.runner my_existing_script.py
python -m playwright_webdriver.runner my_existing_script.py --headless
```

**Via the Python API** (same interception, callable from your own code):

```python
from playwright_webdriver.runner import run_selenium_script

run_selenium_script("my_existing_script.py", headless=True)
```

### Use `PlaywrightWebDriver` directly

```python
from playwright_webdriver import PlaywrightWebDriver, PlaywrightBrowserType
from selenium.webdriver.common.by import By

with PlaywrightWebDriver.create(
    browser_type=PlaywrightBrowserType.CHROMIUM,
    launch_options={"headless": True},
) as driver:
    driver.get("https://example.com")
    heading = driver.find_element(By.TAG_NAME, "h1")
    print(heading.text)  # "Example Domain"
```

---

## Supported Selenium API

### `PlaywrightWebDriver`

| Method / Property | Notes |
|---|---|
| `driver.get(url)` | Navigates to URL |
| `driver.find_element(by, value)` | Returns `PlaywrightWebElement` |
| `driver.find_elements(by, value)` | Returns `list[PlaywrightWebElement]` |
| `driver.execute_script(script, *args)` | Full JS execution; `arguments[N]` supported |
| `driver.current_url` | Current page URL |
| `driver.title` | Page title |
| `driver.page_source` | Full HTML source |
| `driver.maximize_window()` | Sets viewport to 1920×1080 |
| `driver.close()` | Closes current tab |
| `driver.quit()` | Closes browser and releases all resources |
| `driver.navigate()` | Returns navigation object (`back`, `forward`, `refresh`, `to`) |
| `driver.switch_to()` | Returns target locator (`frame`, `window`, `alert`, `default_content`) |
| `driver.manage()` | Returns options object (cookies, timeouts, window) |
| `driver.current_window_handle` | Handle for the current window/tab |
| `driver.window_handles` | All open window/tab handles |

### `PlaywrightWebElement`

| Method / Property | Notes |
|---|---|
| `element.click()` | Clicks the element |
| `element.send_keys(*value)` | Text input; Selenium `Keys` constants supported |
| `element.clear()` | Clears a text field |
| `element.submit()` | Submits the form containing the element |
| `element.find_element(by, value)` | Scoped element search |
| `element.find_elements(by, value)` | Scoped element list |
| `element.get_attribute(name)` | HTML attribute value |
| `element.get_property(name)` | DOM property value |
| `element.get_dom_attribute(name)` | DOM attribute (no fallback to property) |
| `element.text` | Visible text content |
| `element.tag_name` | Element tag name |
| `element.is_displayed()` | `True` if the element is visible |
| `element.is_enabled()` | `True` if the element is enabled |
| `element.is_selected()` | `True` if a checkbox/radio is checked |

### Locator strategies

All standard Selenium `By` strategies are supported:

| `By` constant | Playwright selector |
|---|---|
| `By.ID` | `#value` |
| `By.NAME` | `[name='value']` |
| `By.CLASS_NAME` | `.value` |
| `By.CSS_SELECTOR` | `css=value` |
| `By.XPATH` | `xpath=value` |
| `By.TAG_NAME` | bare tag selector |
| `By.LINK_TEXT` | `a:visible:text-is("value")` (visible only, matching Selenium semantics) |
| `By.PARTIAL_LINK_TEXT` | `a:visible:has-text("value")` (visible only, matching Selenium semantics) |

In addition, `PlaywrightBy.selector(string)` passes a raw Playwright selector string through unchanged, giving you access to Playwright-specific features like `role=`, `text=`, and `:visible` filters:

```python
from playwright_webdriver import PlaywrightBy

btn = driver.find_element(PlaywrightBy.selector("role=button[name='Submit']"))
```

---

## Running Tests

The test suite is a Python port of the original C# NUnit test suite from [Selenium.PlaywrightDriver](https://github.com/thomhurst/Selenium.PlaywrightDriver).

```bash
# Install dev dependencies
poetry install

# Run the full suite (19 tests, all headless)
pytest tests/
```

All tests use local HTML fixtures and an ephemeral HTTP server — no internet connection required.

---

## Examples

The `examples/` directory contains real-world Selenium scripts that run unmodified through the CLI runner:

```bash
python -m playwright_webdriver.runner examples/wikipedia_smoke_test.py
python -m playwright_webdriver.runner examples/apple_homepod_test.py
python -m playwright_webdriver.runner examples/skyscanner_one_way_search_test.py
```

---

## How It Works

The CLI runner monkey-patches `selenium.webdriver.Chrome` (and `Firefox`, `Edge`, `Remote`, etc.) on the **real** `selenium.webdriver` module before `exec()`-ing the script. This means:

- `WebDriverWait`, `expected_conditions`, `Keys`, and all other Selenium helpers continue to import from the real Selenium package — nothing breaks.
- The only substitution is the browser factory: `webdriver.Chrome()` returns a `PlaywrightWebDriver` instance backed by Playwright's Chromium.
- All patches are restored in a `finally` block, so running multiple scripts in the same process is safe.

---

## License

MIT © 2026 HappyPath. See [LICENSE](LICENSE) for details.
