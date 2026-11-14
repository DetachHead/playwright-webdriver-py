from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .playwright_web_driver import PlaywrightWebDriver


class PlaywrightWindow:
    """Port of ``PlaywrightWindow : IWindow``."""

    def __init__(self, driver: PlaywrightWebDriver) -> None:
        self._driver = driver

    def maximize(self) -> None:
        self.size = (1080, 1920)

    def minimize(self) -> None:
        pass  # not supported in Playwright headless

    def full_screen(self) -> None:
        self.maximize()

    @property
    def position(self) -> tuple[int, int]:
        return (0, 0)

    @position.setter
    def position(self, value: tuple[int, int]) -> None:
        pass  # not supported in Playwright headless

    @property
    def size(self) -> tuple[int, int]:
        vs = self._driver.current_page.viewport_size
        if vs:
            return (vs["width"], vs["height"])
        return (0, 0)

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        self._driver.current_page.set_viewport_size({"width": value[0], "height": value[1]})
