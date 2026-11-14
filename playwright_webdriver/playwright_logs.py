from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .playwright_web_driver import PlaywrightWebDriver


class PlaywrightLogs:
    """
    Stub port of ``PlaywrightLogs : ILogs``.
    Playwright does not expose a WebDriver-style log API.
    """

    def __init__(self, driver: PlaywrightWebDriver) -> None:
        self._driver = driver

    def get(self, log_kind: str) -> list[dict]:  # ruff: ignore[no-self-use] TODO: what is this? doesnt seem to map to anything in webdriver
        return []

    @property
    def available_log_types(self) -> list[str]:
        return []
