from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pytest import fixture

from playwright_webdriver import PlaywrightWebDriver

if TYPE_CHECKING:
    from playwright.sync_api import Browser, BrowserContext, Page, Playwright


@fixture
def driver(playwright: Playwright, browser: Browser, context: BrowserContext, page: Page):
    result = PlaywrightWebDriver(playwright, browser, context, page)
    yield result
    # we don't call quit directly because that closes the playwright page/context/browser,
    # which interferes with the teardown of those fixtures
    result._clear_state()


HTML_DIR = Path(__file__).parent / "html_pages"


def page_url(filename: str) -> str:
    """Return a file:// URI for a fixture HTML file."""
    return (HTML_DIR / filename).as_uri()
