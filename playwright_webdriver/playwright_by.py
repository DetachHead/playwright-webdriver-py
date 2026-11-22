from __future__ import annotations

from selenium.webdriver.common.by import By


class PlaywrightBy(By):
    """Extends Selenium's By to allow passing raw Playwright selector strings."""

    def __init__(self, playwright_locator: str):
        self._playwright_locator = playwright_locator

    @property
    def playwright_locator(self) -> str:
        return self._playwright_locator

    @classmethod
    def selector(cls, playwright_locator: str) -> PlaywrightBy:
        """
        Use `PlaywrightBy.selector("text=Submit")` to pass any Playwright-native locator expression
        directly.

        # Example
        ```python
        from playwright_webdriver import PlaywrightBy

        btn = driver.find_element(PlaywrightBy.selector("role=button[name='Submit']"))
        ```
        """
        return cls(playwright_locator)
