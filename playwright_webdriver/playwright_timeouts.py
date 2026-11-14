from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .playwright_web_driver import PlaywrightWebDriver


class PlaywrightTimeouts:
    """Port of ``PlaywrightTimeouts : ITimeouts``."""

    def __init__(self, driver: PlaywrightWebDriver) -> None:
        self._driver = driver

    # ------------------------------------------------------------------
    # implicit_wait  (default action / locator timeout)
    # ------------------------------------------------------------------

    @property
    def implicit_wait(self) -> float:
        """Returns the default timeout in seconds."""
        return 30.0

    @implicit_wait.setter
    def implicit_wait(self, seconds: float) -> None:
        self._driver.current_page.set_default_timeout(seconds * 1000)

    def implicitly_wait(self, seconds: float) -> PlaywrightTimeouts:
        self.implicit_wait = seconds
        return self

    # ------------------------------------------------------------------
    # script_timeout
    # ------------------------------------------------------------------

    @property
    def script_timeout(self) -> float:
        return 30.0

    @script_timeout.setter
    def script_timeout(self, seconds: float) -> None:
        self._driver.current_page.set_default_timeout(seconds * 1000)

    def set_script_timeout(self, seconds: float) -> PlaywrightTimeouts:
        self.script_timeout = seconds
        return self

    # ------------------------------------------------------------------
    # page_load_timeout
    # ------------------------------------------------------------------

    @property
    def page_load_timeout(self) -> float:
        return 30.0

    @page_load_timeout.setter
    def page_load_timeout(self, seconds: float) -> None:
        self._driver.current_page.set_default_navigation_timeout(seconds * 1000)

    def set_page_load_timeout(self, seconds: float) -> PlaywrightTimeouts:
        self.page_load_timeout = seconds
        return self
