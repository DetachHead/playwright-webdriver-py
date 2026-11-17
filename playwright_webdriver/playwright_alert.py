from __future__ import annotations

from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from selenium.webdriver.common.alert import Alert

    from .playwright_web_driver import PlaywrightWebDriver

# https://codeberg.org/DetachHead/playwright-webdriver-py/issues/4
# see comment in playwright_web_driver.py where we do the same thing
if TYPE_CHECKING:
    _BaseAlert = Alert
else:
    _BaseAlert = object


class PlaywrightAlert(_BaseAlert):
    """
    Port of ``PlaywrightAlert : IAlert``.

    Playwright auto-dismisses dialogs via the registered dialog handler on the
    page. Accept/Dismiss are no-ops here — the text of the last dialog is
    captured by that handler and exposed via the ``text`` property.
    """

    def __init__(self, driver: PlaywrightWebDriver) -> None:  # pyrefly: ignore[missing-super-call] not actually extending Alert, see comment above
        self._driver = driver

    @override
    def accept(self) -> None:
        pass  # dialogs are handled automatically by the page dialog handler

    @override
    def dismiss(self) -> None:
        pass  # same as above

    @override
    def send_keys(self, keysToSend: str) -> None:
        raise NotImplementedError("Sending keys to alerts is not supported via Playwright")

    @property
    @override
    def text(self) -> str | None:  # pyrefly: ignore[bad-override] TODO: whose types are wrong here?
        return self._driver._last_alert_text
