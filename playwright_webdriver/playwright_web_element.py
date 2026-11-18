from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast, override

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .keys_mapper import split_into_chunks
from .locator_helpers import get_locator_string

if TYPE_CHECKING:
    from playwright.sync_api import Locator
    from selenium.webdriver.support.relative_locator import RelativeBy

    from playwright_webdriver import PlaywrightWebDriver


# https://codeberg.org/DetachHead/playwright-webdriver-py/issues/4
# see comment in playwright_web_driver.py where we do the same thing
if TYPE_CHECKING:
    _BaseWebElement = WebElement
else:
    _BaseWebElement = object


# register this class as a subclass of `WebElement`.
# this is a disgusting hack, but it's necessary to support robotframework's seleniumlibrary, which
# does `isinstance(..., WebElement)` to determine whether an object is a WebElement (even though
# the completely empty and useless `BaseWebElement` exists seemingly for that purpose, nothing seems
# to ever use it???). see issue linked above
@WebElement.register
class PlaywrightWebElement(_BaseWebElement):
    """
    Selenium WebElement-compatible wrapper around a Playwright ``Locator``.

    Mirrors the C# ``PlaywrightWebElement : IWebElement`` implementation,
    using Playwright's synchronous API instead of the sync-over-async hack
    required in the original C# version.
    """

    def __init__(  # pyrefly: ignore[missing-super-call] not actually extending WebElement, see comments above
        self, locator: Locator, locator_string: str, *, parent: PlaywrightWebDriver
    ) -> None:
        self.__parent = parent
        self._locator = locator
        self._locator_string = locator_string

    @property
    @override
    def parent(self) -> PlaywrightWebDriver:
        return self.__parent

    # TODO: unlike the real WebDriver.id, this doesnt return the same id for different WebElements
    # matching the same element. each newly created PlaywrightWebElement gets a different id
    @property
    @override
    def id(self) -> str:
        return str(id(self))

    # ------------------------------------------------------------------
    # Element discovery
    # ------------------------------------------------------------------

    @override
    def find_element(
        self, by: By | str | RelativeBy = By.ID, value: str | None = None
    ) -> PlaywrightWebElement:
        loc_str = get_locator_string(by, value)
        locator = self._locator.locator(loc_str)
        if locator.count() == 0:
            raise NoSuchElementException(
                f"No element found ({by=}, {value!r}, parent={self.locator})"
            )
        return PlaywrightWebElement(locator.first, loc_str, parent=self.parent)

    @override
    def find_elements(  # pyrefly: ignore[bad-override] variance moment
        self, by: By | str | RelativeBy = By.ID, value: str | None = None
    ) -> list[PlaywrightWebElement]:
        loc_str = get_locator_string(by, value)
        locator = self._locator.locator(loc_str)
        return [PlaywrightWebElement(loc, loc_str, parent=self.parent) for loc in locator.all()]

    # ------------------------------------------------------------------
    # Interactions
    # ------------------------------------------------------------------

    @override
    def click(self) -> None:
        self._locator.click()

    @override
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

    @override
    def clear(self) -> None:
        self._locator.clear()

    @override
    def submit(self) -> None:
        self._locator.dispatch_event("submit")

    # ------------------------------------------------------------------
    # Attribute / property access
    # ------------------------------------------------------------------

    def __get_property(self, name: str) -> str | None:
        return cast(str | None, self.locator.evaluate(f"element => element[{json.dumps(name)}]"))

    @override
    def get_attribute(self, name: str) -> str | None:
        """
        According to the documentation of `WebDriver.get_attribute`, this method actually tries to
        get a property with that name first, then falls back to an attribute of the same name.

        It also says that values like `"true"`/`"false"` are converted to `bool`, but as far as i
        can tell that's a lie.
        """
        value = self.__get_property(name)
        if value is None:
            return self._locator.get_attribute(name)
        return value

    @override
    # bad-override: types on base method are wrong, it can return None
    # explicit-any: dict is untyped in the base method
    def get_property(self, name: str) -> str | bool | PlaywrightWebElement | dict[Any, Any] | None:  # pyrefly: ignore[bad-override, explicit-any]
        return self.__get_property(name)

    @override
    def get_dom_attribute(self, name: str) -> str | None:  # pyrefly: ignore[bad-override] types in base method are wrong, it can return None
        return self._locator.get_attribute(name)

    # TODO: what is this? doesnt seem to exist in WebElement
    def get_dom_property(self, name: str) -> str | None:
        return self.get_attribute(name)

    def get_css_value(self, property_name: str) -> str:
        return self._locator.evaluate(
            f"(element) => window.getComputedStyle(element).getPropertyValue('{property_name}')"
        )

    @override
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
    @override
    def tag_name(self) -> str:
        return self._locator.evaluate("(element) => element.tagName")

    @property
    @override
    def text(self) -> str:
        return self._locator.text_content() or ""

    @override
    def is_enabled(self) -> bool:
        return self._locator.is_enabled()

    # Selenium uses ``is_selected`` for checkboxes/radio
    @override
    def is_selected(self) -> bool:
        return self._locator.is_checked()

    @override
    def is_displayed(self) -> bool:
        return self._locator.is_visible()

    @property
    @override
    def location(self) -> dict[str, int]:
        bb = self._locator.bounding_box() or {"x": 0, "y": 0}
        return {"x": int(bb["x"]), "y": int(bb["y"])}

    @property
    @override
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
