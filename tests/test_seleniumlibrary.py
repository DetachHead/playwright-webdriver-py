from __future__ import annotations

from typing import TYPE_CHECKING

from pytest import MonkeyPatch, fixture
from SeleniumLibrary import SeleniumLibrary
from SeleniumLibrary.keywords.browsermanagement import BrowserManagementKeywords

from tests.conftest import page_url

if TYPE_CHECKING:
    from playwright_webdriver import PlaywrightWebDriver


@fixture
def selenium_library(driver: PlaywrightWebDriver, monkeypatch: MonkeyPatch):
    # by default, selenium will download chromedriver at runtime, so we disable it as a precaution
    # to be 100% certain we're actually testing PlaywrightWebDriver
    monkeypatch.setenv("SE_AVOID_BROWSER_DOWNLOAD", "true")
    result = SeleniumLibrary()
    # currently there's no way to tell type checkers that PlaywrightWebDriver is supposed to be
    # structurally compatible with WebDriver. see https://codeberg.org/DetachHead/playwright-webdriver-py/issues/4
    result.register_driver(driver, "playwright")  # pyrefly: ignore[bad-argument-type]
    return result


def test_find_element(selenium_library: SeleniumLibrary):
    sl = BrowserManagementKeywords(selenium_library)
    sl.go_to(page_url("tag_name.html"))
    element_id = "host"
    assert sl.find_element(element_id).get_attribute("id") == element_id
