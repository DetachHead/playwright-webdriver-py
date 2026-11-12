from selenium.webdriver.common.by import By


class PlaywrightBy(By):
    """
    Extends Selenium's By to allow passing raw Playwright selector strings.
    Use PlaywrightBy.selector("text=Submit") to pass any Playwright-native
    locator expression directly.
    """

    def __init__(self, playwright_locator: str):
        self._playwright_locator = playwright_locator

    @property
    def playwright_locator(self) -> str:
        return self._playwright_locator

    @classmethod
    def selector(cls, playwright_locator: str) -> "PlaywrightBy":
        return cls(playwright_locator)
