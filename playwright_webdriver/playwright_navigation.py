from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .playwright_web_driver import PlaywrightWebDriver


class PlaywrightNavigation:
    """Port of ``PlaywrightNavigation : INavigation``."""

    def __init__(self, driver: "PlaywrightWebDriver") -> None:
        self._driver = driver

    def back(self) -> None:
        self._driver.current_page.go_back()

    def forward(self) -> None:
        self._driver.current_page.go_forward()

    def refresh(self) -> None:
        self._driver.current_page.reload()

    def to(self, url: str) -> None:
        """Alias used by some Selenium scripts: ``driver.navigate().to(url)``."""
        self.go_to_url(url)

    def go_to_url(self, url: str) -> None:
        self._driver.current_page.goto(url)
