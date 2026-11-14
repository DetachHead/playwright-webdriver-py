from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .playwright_web_driver import PlaywrightWebDriver


# TODO: what is this? doesnt seem to map to anything in webdriver
class PlaywrightNetwork:  # ruff: ignore[class-as-data-structure]
    """
    Stub port of ``PlaywrightNetwork : INetwork`` (Selenium 4+).
    Network interception should be done directly via the Playwright
    ``page.route(…)`` / ``context.route(…)`` APIs.
    """

    def __init__(self, driver: PlaywrightWebDriver) -> None:
        self._driver = driver
