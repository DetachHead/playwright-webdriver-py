from __future__ import annotations

from typing import cast

from pytest import MonkeyPatch, fixture
from SeleniumLibrary import SeleniumLibrary
from SeleniumLibrary.keywords.browsermanagement import BrowserManagementKeywords

from playwright_webdriver import PlaywrightWebDriver
from tests.conftest import page_url


@fixture
def selenium_library(driver: PlaywrightWebDriver, monkeypatch: MonkeyPatch):
    # by default, selenium will download chromedriver at runtime, so we disable it as a precaution
    # to be 100% certain we're actually testing PlaywrightWebDriver
    monkeypatch.setenv("SE_AVOID_BROWSER_DOWNLOAD", "true")
    result = SeleniumLibrary()
    result.register_driver(driver, "playwright")
    return result


def test_find_element(selenium_library: SeleniumLibrary):
    sl = BrowserManagementKeywords(selenium_library)
    sl.go_to(page_url("tag_name.html"))
    element_id = "host"
    assert sl.find_element(element_id).get_attribute("id") == element_id


def test_get_element_attribute(selenium_library: SeleniumLibrary):
    sl = BrowserManagementKeywords(selenium_library)
    sl.go_to(page_url("tag_name.html"))
    element_id = "host"
    element = sl.find_element(element_id)
    assert selenium_library.get_element_attribute(element, "id") == element_id


def test_send_keys(selenium_library: SeleniumLibrary):
    sl = BrowserManagementKeywords(selenium_library)
    sl.go_to(page_url("form_submit.html"))
    element_id = "input1"
    value = "asdfasdf"
    selenium_library.press_keys(element_id, value)
    selenium_library.press_keys(element_id, "CTRL+aCTRL+c")

    driver = cast(PlaywrightWebDriver, selenium_library.driver)
    driver.context.grant_permissions(["clipboard-read"])
    clipboard_content = driver.current_page.evaluate("() => navigator.clipboard.readText()")
    assert clipboard_content == value
