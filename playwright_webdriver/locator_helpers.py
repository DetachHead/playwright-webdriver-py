from __future__ import annotations

from selenium.webdriver.common.by import By

from .playwright_by import PlaywrightBy

# Maps the string that selenium.webdriver.common.by.By stores as the
# "using" / mechanism value to the Playwright selector prefix.
_MECHANISM_MAP: dict[str, str | None] = {
    By.XPATH: "xpath",
    By.CSS_SELECTOR: "css",
    By.TAG_NAME: None,  # Playwright accepts bare tag names as CSS
    By.ID: None,  # handled explicitly → #id
    By.NAME: None,  # handled explicitly → [name='…']
    By.CLASS_NAME: None,  # handled explicitly → .classname
    By.LINK_TEXT: None,  # handled explicitly → a:text-is("…")
    By.PARTIAL_LINK_TEXT: None,  # handled explicitly → a:has-text("…")
}


def get_locator_string(by: By | tuple[str, str] | str, value: str | None = None) -> str:
    """
    Convert a Selenium ``By`` locator into a Playwright selector string.

    Accepts three calling conventions:

    1. ``get_locator_string(PlaywrightBy.selector("text=Submit"))``
    2. ``get_locator_string(By.ID, "my-id")``          - (strategy, value) pair
    3. ``get_locator_string((By.ID, "my-id"))``         - tuple

    Returns a string suitable for ``page.locator(…)`` or ``locator.locator(…)``.
    """
    # PlaywrightBy carries a raw Playwright locator string — use it directly.
    if isinstance(by, PlaywrightBy):
        return by.playwright_locator

    # Normalise (strategy, value) calling conventions.
    if isinstance(by, tuple):
        by, value = by

    strategy: str = by  # By constants are plain strings in the Python library
    criteria: str = value or ""

    if strategy == By.XPATH:
        return f"xpath={criteria}"

    if strategy == By.CSS_SELECTOR:
        return f"css={criteria}"

    if strategy == By.TAG_NAME:
        return criteria

    if strategy == By.ID:
        return f"#{criteria}"

    if strategy == By.NAME:
        return f"[name='{criteria}']"

    if strategy == By.CLASS_NAME:
        return f".{criteria}"

    if strategy == By.LINK_TEXT:
        # Real Selenium By.LINK_TEXT only matches displayed (visible) links.
        return f'a:visible:text-is("{criteria}")'

    if strategy == By.PARTIAL_LINK_TEXT:
        # Real Selenium By.PARTIAL_LINK_TEXT only matches displayed (visible) links.
        return f'a:visible:has-text("{criteria}")'

    raise ValueError(f"Unknown Selenium locator strategy: {strategy!r} - {criteria!r}")
