from __future__ import annotations

from typing import TYPE_CHECKING, Final

from selenium.webdriver.remote.webelement import WebElement

from .keys_mapper import split_into_chunks
from .locator_helpers import get_locator_string

if TYPE_CHECKING:
    from playwright.sync_api import Locator

    from playwright_webdriver import PlaywrightWebDriver


# register this class as a subclass of `WebElement`.
#
# this is a disgusting hack, but it's necessary to support robotframework's seleniumlibrary, which
# does `isinstance(..., WebElement)` to determine whether anh object is a WebElement (even though
# the completely empty and useless `BaseWebElement` exists seemingly for that purpose, nothing seems
# to ever use it???).
#
# ideally there would be a `WebElement` ABC/Protocol or something that `PlaywrightWebElement` could
# implement. alternatively we could just extend `WebElement` instead of using this wacky subclass
# registration thing, but we do this to prevent anything from unintentionally calling the real
# `WebElement` in case there's anything from that class we haven't implemented.
# see https://codeberg.org/DetachHead/playwright-webdriver-py/issues/4
@WebElement.register
class PlaywrightWebElement:
    """
    Selenium WebElement-compatible wrapper around a Playwright ``Locator``.

    Mirrors the C# ``PlaywrightWebElement : IWebElement`` implementation,
    using Playwright's synchronous API instead of the sync-over-async hack
    required in the original C# version.
    """

    def __init__(
        self, locator: Locator, locator_string: str, *, parent: PlaywrightWebDriver
    ) -> None:
        self.parent: Final[PlaywrightWebDriver] = parent
        self._locator = locator
        self._locator_string = locator_string

    # ------------------------------------------------------------------
    # Element discovery
    # ------------------------------------------------------------------

    def find_element(self, by: str, value: str) -> PlaywrightWebElement:
        loc_str = get_locator_string(by, value)
        return PlaywrightWebElement(
            self._locator.locator(loc_str).first, loc_str, parent=self.parent
        )

    def find_elements(self, by: str, value: str) -> list[PlaywrightWebElement]:
        loc_str = get_locator_string(by, value)
        locator = self._locator.locator(loc_str)
        return [PlaywrightWebElement(loc, loc_str, parent=self.parent) for loc in locator.all()]

    # ------------------------------------------------------------------
    # Interactions
    # ------------------------------------------------------------------

    def click(self) -> None:
        self._locator.click()

    def send_keys(self, *value: str) -> None:
        text = "".join(str(v) for v in value)
        if self.get_attribute("type") == "file":
            self._locator.set_input_files(text)
            return
        chunks = split_into_chunks(text)
        if not chunks:
            return
        # If the entire input is plain text with no special keys, use fill().
        if len(chunks) == 1 and chunks[0][0] == "text":
            self._locator.fill(chunks[0][1])
            return
        # Mixed or keys-only: type plain text incrementally, press special keys.
        for kind, val in chunks:
            if kind == "text":
                self._locator.press_sequentially(val)
            else:
                self._locator.press(val)

    def clear(self) -> None:
        self._locator.clear()

    def submit(self) -> None:
        self._locator.dispatch_event("submit")

    # ------------------------------------------------------------------
    # Attribute / property access
    # ------------------------------------------------------------------

    def get_attribute(self, name: str) -> str | None:
        return self._locator.get_attribute(name)

    def get_property(self, name: str) -> str | None:
        return self.get_attribute(name)

    def get_dom_attribute(self, name: str) -> str | None:
        return self.get_attribute(name)

    def get_dom_property(self, name: str) -> str | None:
        return self.get_attribute(name)

    def get_css_value(self, property_name: str) -> str:
        return self._locator.evaluate(
            f"(element) => window.getComputedStyle(element).getPropertyValue('{property_name}')"
        )

    def value_of_css_property(self, property_name: str) -> str:
        return self.get_css_value(property_name)

    # ------------------------------------------------------------------
    # Shadow DOM
    # ------------------------------------------------------------------

    def get_shadow_root(self) -> PlaywrightWebElement:
        """Return self — shadow DOM children are found via playwright selectors."""
        return self

    # ------------------------------------------------------------------
    # Properties (mirrors IWebElement members)
    # ------------------------------------------------------------------

    @property
    def tag_name(self) -> str:
        return self._locator.evaluate("(element) => element.tagName")

    @property
    def text(self) -> str:
        return self._locator.text_content() or ""

    def is_enabled(self) -> bool:
        return self._locator.is_enabled()

    # Selenium uses ``is_selected`` for checkboxes/radio
    def is_selected(self) -> bool:
        return self._locator.is_checked()

    def is_displayed(self) -> bool:
        return self._locator.is_visible()

    @property
    def location(self) -> dict[str, int]:
        bb = self._locator.bounding_box() or {"x": 0, "y": 0}
        return {"x": int(bb["x"]), "y": int(bb["y"])}

    @property
    def size(self) -> dict[str, int]:
        bb = self._locator.bounding_box() or {"width": 0, "height": 0}
        return {"width": int(bb["width"]), "height": int(bb["height"])}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @property
    def locator(self) -> Locator:
        return self._locator

    @property
    def locator_string(self) -> str:
        return self._locator_string
