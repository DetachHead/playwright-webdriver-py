---
weight: -1
---

# Use `PlaywrightWebDriver` directly

```python
from playwright_webdriver import PlaywrightWebDriver, PlaywrightBrowserType
from selenium.webdriver.common.by import By

with PlaywrightWebDriver.create(
    browser_type=PlaywrightBrowserType.CHROMIUM, launch_options={"headless": True}
) as driver:
    driver.get("https://example.com")
    heading = driver.find_element(By.TAG_NAME, "h1")
    print(heading.text)  # "Example Domain"
```
