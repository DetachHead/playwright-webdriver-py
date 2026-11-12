from __future__ import annotations

from typing import TYPE_CHECKING

from selenium.common.exceptions import NoSuchFrameException, NoSuchWindowException
from selenium.webdriver.common.by import By

from .locator_helpers import get_locator_string
from .playwright_alert import PlaywrightAlert
from .playwright_by import PlaywrightBy
from .playwright_web_element import PlaywrightWebElement

if TYPE_CHECKING:
    from .playwright_web_driver import PlaywrightWebDriver


class PlaywrightTargetLocator:
    """Port of ``PlaywrightTargetLocator : ITargetLocator``."""

    def __init__(self, driver: "PlaywrightWebDriver") -> None:
        self._driver = driver

    # ------------------------------------------------------------------
    # Frame switching
    # ------------------------------------------------------------------

    def frame(self, reference) -> "PlaywrightWebDriver":
        """
        Switch to a frame by index (int), name/id (str), or WebElement.
        """
        if isinstance(reference, int):
            return self._frame_by_index(reference)
        if isinstance(reference, str):
            return self._frame_by_name(reference)
        if isinstance(reference, PlaywrightWebElement):
            return self._frame_by_element(reference)
        raise ValueError(f"Unsupported frame reference type: {type(reference)}")

    def _frame_by_index(self, index: int) -> "PlaywrightWebDriver":
        frames = self._driver.current_page.frames
        if index >= len(frames):
            raise NoSuchFrameException(f"No frame at index {index}")
        frame_locator = frames[index].frame_locator(":root").first
        return self._driver._set_frame(frame_locator)

    def _frame_by_name(self, name: str) -> "PlaywrightWebDriver":
        loc_str = get_locator_string(By.NAME, name)
        if self._driver.current_frame_locators:
            frame_locator = self._driver.current_frame_locators[-1].frame_locator(loc_str).first
        else:
            frame_locator = self._driver.current_page.frame_locator(loc_str).first

        if frame_locator.owner.count() == 0:
            raise NoSuchFrameException(f"No frame named {name!r}")
        return self._driver._set_frame(frame_locator)

    def _frame_by_element(self, element: PlaywrightWebElement) -> "PlaywrightWebDriver":
        tag = element.tag_name.upper()
        if tag not in ("IFRAME", "FRAME"):
            raise NoSuchFrameException(f"Element is not a frame: {tag}")
        frame_locator = self._driver.current_page.frame_locator(element.locator_string).first
        if frame_locator.owner.count() == 0:
            raise NoSuchFrameException(f"No frame for locator {element.locator_string!r}")
        return self._driver._set_frame(frame_locator)

    def parent_frame(self) -> "PlaywrightWebDriver":
        fl = self._driver.current_frame_locators
        if fl:
            fl.pop()
        return self._driver

    def default_content(self) -> "PlaywrightWebDriver":
        self._driver.current_page = self._driver.original_page
        return self._driver

    # ------------------------------------------------------------------
    # Window switching
    # ------------------------------------------------------------------

    def window(self, window_name: str) -> "PlaywrightWebDriver":
        page = self._driver.key_to_page.get(window_name)
        if page is None:
            raise NoSuchWindowException(f"No window with handle: {window_name!r}")
        self._driver.current_page = page
        return self._driver

    def new_window(self, type_hint: str = "window") -> "PlaywrightWebDriver":
        """Open a new tab/window (Selenium 4 API)."""
        self._driver._new_page()
        return self._driver

    # ------------------------------------------------------------------
    # Other
    # ------------------------------------------------------------------

    def active_element(self) -> PlaywrightWebElement:
        loc_str = "*:focus"
        locator = self._driver.current_page.locator(loc_str).first
        return PlaywrightWebElement(locator, loc_str)

    def alert(self) -> PlaywrightAlert:
        return PlaywrightAlert(self._driver)
