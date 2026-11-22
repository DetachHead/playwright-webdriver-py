# Usage with RobotFramework / SeleniumLibrary

To use `playwright-webdriver-py` with `SeleniumLibrary`, you can register its driver:

!!! example

    ```py
    from SeleniumLibrary import SeleniumLibrar
    from playwright_webdriver import PlaywrightWebDriver, PlaywrightBrowserType
    from selenium.webdriver.common.by import By

    with PlaywrightWebDriver.create(browser_type=PlaywrightBrowserType.CHROMIUM) as driver:
        selenium = SeleniumLibrary()
        selenium.register_driver(driver, "playwright")
        selenium.goto("https://google.com")
    ```

!!! tip

    This example uses Python instead of [RobotFramework](https://robotframework.org/) syntax. This is because I despise that languguage and cannot be bothered trying to figure out how to do something as simple as instantiating a class and calling a method (if you know how to do it, feel free to [submit a PR](https://github.com/DetachHead/playwright-webdriver-py/pulls))

    If you are forced to use RobotFramework, I recommend using my plugin [`pytest-robotframework`](https://detachhead.github.io/pytest-robotframework) so you can just write your tests in Python without having to deal with the language.
