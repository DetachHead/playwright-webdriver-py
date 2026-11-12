from __future__ import annotations

from typing import TYPE_CHECKING

from .playwright_cookie_jar import PlaywrightCookieJar
from .playwright_logs import PlaywrightLogs
from .playwright_network import PlaywrightNetwork
from .playwright_timeouts import PlaywrightTimeouts
from .playwright_window import PlaywrightWindow

if TYPE_CHECKING:
    from .playwright_web_driver import PlaywrightWebDriver


class PlaywrightOptions:
    """Port of ``PlaywrightOptions : IOptions``."""

    def __init__(self, driver: "PlaywrightWebDriver") -> None:
        self._driver = driver

    def timeouts(self) -> PlaywrightTimeouts:
        return PlaywrightTimeouts(self._driver)

    @property
    def cookies(self) -> PlaywrightCookieJar:
        return PlaywrightCookieJar(self._driver)

    @property
    def window(self) -> PlaywrightWindow:
        return PlaywrightWindow(self._driver)

    @property
    def logs(self) -> PlaywrightLogs:
        return PlaywrightLogs(self._driver)

    @property
    def network(self) -> PlaywrightNetwork:
        return PlaywrightNetwork(self._driver)
