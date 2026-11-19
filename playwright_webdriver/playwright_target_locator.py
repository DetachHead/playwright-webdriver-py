from __future__ import annotations

from typing import TYPE_CHECKING, override

from selenium.common.exceptions import NoSuchFrameException, NoSuchWindowException
from selenium.webdriver.common.by import By

from .locator_helpers import get_locator_string
from .playwright_alert import PlaywrightAlert
from .playwright_web_element import PlaywrightWebElement

if TYPE_CHECKING:
    from selenium.webdriver.remote.switch_to import SwitchTo

    from .playwright_web_driver import PlaywrightWebDriver

# https://codeberg.org/DetachHead/playwright-webdriver-py/issues/4
# see comment in playwright_web_driver.py where we do the same thing
if TYPE_CHECKING:
    _BaseSwitchTo = SwitchTo
else:
    _BaseSwitchTo = object


class PlaywrightTargetLocator(_BaseSwitchTo):
    """Port of ``PlaywrightTargetLocator : ITargetLocator``."""

    # pyrefly: ignore[missing-super-call]
    def __init__(self, driver: PlaywrightWebDriver) -> None:
        self._driver: PlaywrightWebDriver = driver  # pyrefly: ignore[bad-override-mutable-attribute] messed up types in base class

    # ------------------------------------------------------------------
    # Frame switching
    # ------------------------------------------------------------------

    @override
    def frame(self, frame_reference) -> None:
        """
        Switch to a frame by index (int), name/id (str), or WebElement.
        """
        if isinstance(frame_reference, int):
            self._frame_by_index(frame_reference)
        elif isinstance(frame_reference, str):
            self._frame_by_name(frame_reference)
        elif isinstance(frame_reference, PlaywrightWebElement):
            self._frame_by_element(frame_reference)
        else:
            raise TypeError(f"Unsupported frame reference type: {type(frame_reference)}")

    def _frame_by_index(self, index: int) -> None:
        frames = self._driver.current_page.frames
        if index >= len(frames):
            raise NoSuchFrameException(f"No frame at index {index}")
        frame_locator = frames[index].frame_locator(":root").first
        self._driver._set_frame(frame_locator)

    def _frame_by_name(self, name: str) -> None:
        loc_str = get_locator_string(By.NAME, name)
        if self._driver.current_frame_locators:
            frame_locator = self._driver.current_frame_locators[-1].frame_locator(loc_str).first
        else:
            frame_locator = self._driver.current_page.frame_locator(loc_str).first

        if frame_locator.owner.count() == 0:
            raise NoSuchFrameException(f"No frame named {name!r}")
        self._driver._set_frame(frame_locator)

    def _frame_by_element(self, element: PlaywrightWebElement) -> None:
        tag = element.tag_name.upper()
        if tag not in {"IFRAME", "FRAME"}:
            raise NoSuchFrameException(f"Element is not a frame: {tag}")
        frame_locator = self._driver.current_page.frame_locator(element.locator_string).first
        if frame_locator.owner.count() == 0:
            raise NoSuchFrameException(f"No frame for locator {element.locator_string!r}")
        self._driver._set_frame(frame_locator)

    @override
    def parent_frame(self) -> None:
        fl = self._driver.current_frame_locators
        if fl:
            fl.pop()

    @override
    def default_content(self) -> None:
        self._driver.current_page = self._driver.original_page

    # ------------------------------------------------------------------
    # Window switching
    # ------------------------------------------------------------------

    @override
    def window(self, window_name: str) -> None:
        page = self._driver.key_to_page.get(window_name)
        if page is None:
            raise NoSuchWindowException(f"No window with handle: {window_name!r}")
        self._driver.current_page = page

    @override
    def new_window(self, type_hint: str | None = None) -> None:
        """Open a new tab/window (Selenium 4 API)."""
        self._driver._new_page()

    # ------------------------------------------------------------------
    # Other
    # ------------------------------------------------------------------

    @property
    @override
    def active_element(self) -> PlaywrightWebElement:
        loc_str = "*:focus"
        locator = self._driver.current_page.locator(loc_str).first
        # TODO: should this resolve?
        return PlaywrightWebElement(locator, loc_str, parent=self._driver, resolve=False)

    @property
    @override
    def alert(self) -> PlaywrightAlert:
        return PlaywrightAlert(self._driver)
