from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .playwright_web_driver import PlaywrightWebDriver


class PlaywrightAlert:
    """
    Port of ``PlaywrightAlert : IAlert``.

    Playwright auto-dismisses dialogs via the registered dialog handler on the
    page. Accept/Dismiss are no-ops here — the text of the last dialog is
    captured by that handler and exposed via the ``text`` property.
    """

    def __init__(self, driver: PlaywrightWebDriver) -> None:
        self._driver = driver

    def accept(self) -> None:
        pass  # dialogs are handled automatically by the page dialog handler

    def dismiss(self) -> None:
        pass  # same as above

    def send_keys(self, keys_to_send: str) -> None:
        raise NotImplementedError("Sending keys to alerts is not supported via Playwright")

    @property
    def text(self) -> str | None:
        return self._driver._last_alert_text
