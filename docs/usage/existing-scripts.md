# Run an existing Selenium script unchanged

!!! warning

    This method relies on hacky runtime patching and is not recommended. Try [using `PlaywrightWebDriver` directly](python-api.md) instead.

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

## Via the CLI runner

```bash
python -m playwright_webdriver.runner my_existing_script.py
python -m playwright_webdriver.runner my_existing_script.py --headless
```

## Via the Python API

```python
from playwright_webdriver.runner import run_selenium_script

run_selenium_script("my_existing_script.py", headless=True)
```
