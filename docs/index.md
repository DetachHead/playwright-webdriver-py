# playwright-webdriver-py

`playwright-webdriver-py` aims to be a drop-in compatibility layer that implements the Selenium WebDriver Python API over [Playwright's](https://playwright.dev/) synchronous API. Drop it in and your existing `webdriver.Chrome()` scripts run backed by Playwright; faster, more reliable, and without the ChromeDriver version-matching headache.

!!! info "Disclaimer"

    Not every aspect of the selenium `WebDriver` has been re-implemented yet, and there are subtle differences in behavior due to differences in how Playwright works. If you encounter any problems, please [open an issue](https://github.com/DetachHead/playwright-webdriver-py/issues).
