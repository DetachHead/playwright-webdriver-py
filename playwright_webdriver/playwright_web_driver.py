from __future__ import annotations

import contextlib
import re
import uuid
from typing import TYPE_CHECKING, Any, Self, override

from playwright.sync_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Page,
    Playwright,
    sync_playwright,
)
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from .locator_helpers import get_locator_string
from .playwright_browser_type import PlaywrightBrowserType
from .playwright_navigation import PlaywrightNavigation
from .playwright_options import PlaywrightOptions
from .playwright_target_locator import PlaywrightTargetLocator
from .playwright_web_element import PlaywrightWebElement

if TYPE_CHECKING:
    from types import TracebackType

    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support.relative_locator import RelativeBy


_RE_ARGUMENTS = re.compile(r"arguments\[(?P<number>[0-9]+)\]")


# we pretend to extend WebDriver to trick type checkers into thinking PlaywrightWebDriver is a
# subtype, since there's no ABC/Protocol for WebDriver we can use. we avoid doing this at runtime
# to prevent anything from unintentionally calling the real `WebDriver` in case there's anything
# from that class we haven't implemented. see https://codeberg.org/DetachHead/playwright-webdriver-py/issues/4
if TYPE_CHECKING:
    _BaseWebDriver = WebDriver
else:
    _BaseWebDriver = object


class PlaywrightWebDriver(_BaseWebDriver):
    """
    Selenium WebDriver-compatible driver backed by Playwright's synchronous API.

    Port of the C# ``PlaywrightWebDriver : IWebDriver, IJavaScriptExecutor``
    class. Uses Playwright's native ``sync_api`` to avoid the sync-over-async
    anti-pattern present in the original C# implementation.

    Typical usage::

        driver = PlaywrightWebDriver.create()
        driver.get("https://example.com")
        el = driver.find_element(By.ID, "submit-btn")
        el.click()
        driver.quit()

    Or as a context manager::

        with PlaywrightWebDriver.create() as driver:
            driver.get("https://example.com")
    """

    def __init__(  # pyrefly: ignore[missing-super-call] not actually extending WebDriver, see comment above
        self, playwright: Playwright, browser: Browser, context: BrowserContext, current_page: Page
    ) -> None:
        self._playwright = playwright
        self._playwright_browser = browser
        self._context = context
        self._original_page = current_page

        # page handle bookkeeping  {handle_str: Page}
        self._key_to_page: dict[str, Page] = {}
        self._window_handles_in_order: list[str] = []

        # frame stack for SwitchTo().frame(…)
        self._current_frame_locators: list = []

        # last alert text captured by the dialog handler
        self._last_alert_text: str | None = None

        # register initial page
        initial_key = str(uuid.uuid4())
        self._key_to_page[initial_key] = current_page
        self._current_page: Page = current_page
        self._set_current_page(current_page)

        # listen for popups (new windows/tabs opened by the page)
        current_page.on("popup", self._on_popup)
        self._register_alert_handler(current_page)

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        browser_type: PlaywrightBrowserType = PlaywrightBrowserType.CHROMIUM,
        launch_options: dict | None = None,
        context_options: dict | None = None,
    ) -> PlaywrightWebDriver:
        """
        Create a ``PlaywrightWebDriver`` using a synchronous Playwright context.

        The caller is responsible for calling ``quit()`` (or using the driver
        as a context manager) to release browser resources.
        """
        pw = sync_playwright().start()

        browser_type_obj: BrowserType = getattr(pw, browser_type.value)
        browser = browser_type_obj.launch(**(launch_options or {}))
        context = browser.new_context(**(context_options or {}))
        page = context.new_page()

        return cls(pw, browser, context, page)

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    @override
    def __enter__(self) -> Self:
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.quit()

    # ------------------------------------------------------------------
    # Page / window management (internal)
    # ------------------------------------------------------------------

    def _set_current_page(self, page: Page) -> None:
        self._current_page = page
        self._current_frame_locators.clear()
        handle = self._page_to_key()[page]
        if handle not in self._window_handles_in_order:
            self._window_handles_in_order.append(handle)
        page.bring_to_front()

    def _page_to_key(self) -> dict[Page, str]:
        return {v: k for k, v in self._key_to_page.items()}

    def _on_popup(self, page: Page) -> None:
        key = str(uuid.uuid4())
        self._key_to_page[key] = page
        page.on("popup", self._on_popup)
        self._register_alert_handler(page)

    def _register_alert_handler(self, page: Page) -> None:
        def _handler(dialog: Any) -> None:
            self._last_alert_text = dialog.message
            dialog.dismiss()

        page.on("dialog", _handler)

    def _new_page(self) -> PlaywrightWebDriver:
        page = self._context.new_page()
        key = str(uuid.uuid4())
        self._key_to_page[key] = page
        self._set_current_page(page)
        self._register_alert_handler(page)
        return self

    def _set_frame(self, frame_locator: Any) -> None:
        self._current_frame_locators.append(frame_locator)

    # ------------------------------------------------------------------
    # Core WebDriver interface
    # ------------------------------------------------------------------

    @override
    def get(self, url: str) -> None:
        """Navigate to ``url`` (Selenium convention: ``driver.get(url)``)."""
        self._current_page.goto(url)

    @override
    def find_element(
        self, by: str | By | RelativeBy = By.ID, value: str | None = None
    ) -> PlaywrightWebElement:
        loc_str = get_locator_string(by, value)

        if self._current_frame_locators:
            locator = self._current_frame_locators[-1].locator(loc_str).first
        else:
            locator = self._current_page.locator(loc_str).first

        if locator.count() == 0:
            raise NoSuchElementException(f"No element found for ({by!r}, {value!r})")

        return PlaywrightWebElement(locator, loc_str, parent=self)

    @override
    def find_elements(  # pyrefly: ignore[bad-override] variance moment
        self, by: By | RelativeBy | str = By.ID, value: str | None = None
    ) -> list[PlaywrightWebElement]:
        loc_str = get_locator_string(by, value)

        if self._current_frame_locators:
            locator = self._current_frame_locators[-1].locator(loc_str)
        else:
            locator = self._current_page.locator(loc_str)

        return [PlaywrightWebElement(loc, loc_str, parent=self) for loc in locator.all()]

    @override
    def close(self) -> None:
        """Close the current window/tab."""
        p2k = self._page_to_key()
        handle = p2k[self._current_page]
        self._current_page.close()
        del self._key_to_page[handle]
        self._window_handles_in_order = [h for h in self._window_handles_in_order if h != handle]

        if not self._key_to_page:
            self._quit_resources()
        else:
            last_handle = self._window_handles_in_order[-1]
            self._set_current_page(self._key_to_page[last_handle])

    @override
    def quit(self) -> None:
        """Close the browser and release all resources."""
        self._quit_resources()

    @override
    def maximize_window(self) -> None:
        """Maximize the browser viewport (mirrors driver.maximize_window() in Selenium)."""
        self._current_page.set_viewport_size({"width": 1920, "height": 1080})

    def _clear_state(self) -> None:
        self._key_to_page.clear()
        self._window_handles_in_order.clear()

    def _quit_resources(self) -> None:
        self._clear_state()
        with contextlib.suppress(Exception):
            self._context.close()
        with contextlib.suppress(Exception):
            self._playwright_browser.close()
        with contextlib.suppress(Exception):
            self._playwright.stop()

    # ------------------------------------------------------------------
    # Options / Navigation / SwitchTo
    # ------------------------------------------------------------------

    def manage(self) -> PlaywrightOptions:
        return PlaywrightOptions(self)

    def navigate(self) -> PlaywrightNavigation:
        return PlaywrightNavigation(self)

    @property
    @override
    def switch_to(self) -> PlaywrightTargetLocator:
        return PlaywrightTargetLocator(self)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    @override
    def current_url(self) -> str:
        return self._current_page.url

    @property
    @override
    def title(self) -> str:
        return self._current_page.title()

    @property
    @override
    def page_source(self) -> str:
        return self._current_page.content()

    @property
    @override
    def current_window_handle(self) -> str:
        return self._page_to_key()[self._current_page]

    @property
    @override
    def window_handles(self) -> list[str]:
        return list(self._key_to_page.keys())

    # URL setter — mirrors ``driver.url = "…"`` in the C# version and
    # the Selenium Python ``driver.get()`` pattern.
    @property
    def url(self) -> str:
        return self.current_url

    @url.setter
    def url(self, value: str) -> None:
        self._current_page.goto(value)

    # ------------------------------------------------------------------
    # JavaScript execution
    # ------------------------------------------------------------------

    @override
    def execute_script(self, script: str, *args: Any) -> Any:
        script, args = self._convert_script(script, list(args))
        if self._current_frame_locators:
            return self._current_frame_locators[-1].owner.evaluate(script, args)
        return self._current_page.evaluate(script, args)

    @override
    def execute_async_script(self, script: str, *args: Any) -> Any:
        return self.execute_script(script, *args)

    @staticmethod
    def _convert_script(script: str, args: list[Any]) -> tuple[str, list[Any]]:
        # Replace PlaywrightWebElement args with their element handles
        converted_args: list[Any] = []
        for arg in args:
            if isinstance(arg, PlaywrightWebElement):
                converted_args.append(arg.locator.element_handle())
            else:
                converted_args.append(arg)

        # Strip leading "return " — Playwright uses expression mode
        script = script.removeprefix("return ")

        # Wrap scripts that reference ``arguments[N]`` so Playwright receives
        # them as a named parameter.
        if _RE_ARGUMENTS.search(script):
            script = f"arguments => {script}"

        return script, converted_args

    # ------------------------------------------------------------------
    # Expose internals for support classes
    # ------------------------------------------------------------------

    @property
    def current_page(self) -> Page:
        return self._current_page

    @current_page.setter
    def current_page(self, page: Page) -> None:
        self._set_current_page(page)

    @property
    def original_page(self) -> Page:
        return self._original_page

    @property
    def context(self) -> BrowserContext:
        return self._context

    @property
    def key_to_page(self) -> dict[str, Page]:
        return self._key_to_page

    @property
    def current_frame_locators(self) -> list:
        return self._current_frame_locators
