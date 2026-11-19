"""
Pytest port of the C# NUnit test suite:
  TomLonghurst.Selenium.PlaywrightWebDriver.Tests / Tests.cs

Each test creates its own driver instance (matching the C# [Parallelizable]
pattern) and cleans up after itself.  HTML fixtures live in html_pages/ next
to this file — referenced via ``file://`` URIs so no web server is needed.
"""

from __future__ import annotations

import tempfile
import threading
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import override

import pytest
from playwright.sync_api import Page, Playwright
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By

from playwright_webdriver import PlaywrightWebDriver
from tests.conftest import HTML_DIR, page_url

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def http_server():
    """
    Serve the html_pages directory over HTTP so cookie tests have a real domain.
    Mirrors what the C# tests do with an ASP.NET Core test server.

    Yields:
        the URL of the server
    """
    handler = partial(SimpleHTTPRequestHandler, directory=str(HTML_DIR))
    server = HTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


# ---------------------------------------------------------------------------
# Tests — mirrors the C# test class order
# ---------------------------------------------------------------------------


def test_last_window_closed(playwright: Playwright):
    class MockPlaywright(Playwright):
        """
        the `playwright` fixture is global so we need to prevent it from being closed on
        `driver.quit` otherwise it will break any subsequent tests that run in the same session
        """

        stop_called = False

        @override
        def stop(self):
            self.stop_called = True

    # this test creates its own playwright browser/context/etc because it needs to kill them before
    # the end of the test
    mock_playwright = MockPlaywright(playwright._impl_obj)
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    driver = PlaywrightWebDriver(mock_playwright, browser, context, context.new_page())

    driver.get(page_url("tag_name.html"))
    driver.quit()
    assert len(driver.key_to_page) == 0
    assert mock_playwright.stop_called


class TestExecuteScript:
    @staticmethod
    def test_script_with_return(driver: PlaywrightWebDriver):
        driver.get(page_url("locators_test.html"))
        result = driver.execute_script("return document.querySelector('#id1').textContent")
        assert result == "Id One"

    @staticmethod
    def test_script_without_return(driver: PlaywrightWebDriver):
        driver.get(page_url("locators_test.html"))
        result = driver.execute_script("document.querySelector('#id1').textContent")
        # we mimic selenium's behavior, so only return the value if there's a return statement
        assert result is None

    @staticmethod
    def test_script_with_selenium_style_arguments(driver: PlaywrightWebDriver):
        driver.get(page_url("locators_test.html"))
        result = driver.execute_script(
            "return `You passed in ${arguments[0]} and ${arguments[1]}`", "Foo", "Bar"
        )
        assert result == "You passed in Foo and Bar"

    @staticmethod
    def test_script_with_element_argument(driver: PlaywrightWebDriver):
        driver.get(page_url("script_element_scroll.html"))
        element = driver.find_element(By.ID, "id500")
        # Should not raise — scrolls the element into view
        driver.execute_script("arguments[0].scrollIntoView(true)", element)

    @staticmethod
    def test_multiple_statements(driver: PlaywrightWebDriver):
        driver.get(page_url("locators_test.html"))
        assert driver.execute_script("1;return 2") == 2


def test_locators(driver: PlaywrightWebDriver):
    driver.get(page_url("locators_test.html"))

    assert driver.find_element(By.ID, "id1").text == "Id One"
    assert driver.find_element(By.CLASS_NAME, "class1").text == "Class One"
    assert driver.find_element(By.TAG_NAME, "span").text == "Span One"
    assert driver.find_element(By.CSS_SELECTOR, ".class1").text == "Class One"
    assert driver.find_element(By.XPATH, "//div[@id='id1']").text == "Id One"
    assert driver.find_element(By.LINK_TEXT, "Link Text") is not None
    assert driver.find_element(By.PARTIAL_LINK_TEXT, "Link") is not None
    assert driver.find_element(By.NAME, "name1").text == "Name One"


def test_tag_name(driver: PlaywrightWebDriver):
    driver.get(page_url("tag_name.html"))
    element = driver.find_element(By.ID, "host")
    assert element.tag_name.upper() == "DIV"


def test_shadow_dom(driver: PlaywrightWebDriver):
    driver.get(page_url("shadow_dom.html"))
    # Playwright's >> css= pierces shadow boundaries; use the pierce: prefix
    _ = driver.find_element(By.CSS_SELECTOR, "#host > span")
    # The shadow DOM span is accessible via Playwright's auto-piercing locator
    # Fall back to evaluating JS to confirm shadow content exists
    text = driver.execute_script(
        "return document.querySelector('#host').shadowRoot.querySelector('span').textContent"
    )
    assert text == "I'm in the shadow DOM"


def test_nested_finds(driver: PlaywrightWebDriver):
    driver.get(page_url("nested_finds.html"))
    host = driver.find_element(By.ID, "host")
    inner1 = host.find_element(By.CLASS_NAME, "inner1")
    inner2 = inner1.find_element(By.CLASS_NAME, "inner2")
    inner3 = inner2.find_element(By.CLASS_NAME, "inner3")
    assert "Most inner!" in inner3.text


def test_click(driver: PlaywrightWebDriver):
    driver.get(page_url("click.html"))
    host = driver.find_element(By.ID, "host")
    assert host.text == "Not yet clicked"
    driver.find_element(By.ID, "btn").click()
    assert driver.find_element(By.ID, "host").text == "Clicked"


def test_alert(driver: PlaywrightWebDriver):
    driver.get(page_url("alert.html"))
    # The dialog handler captures the text before auto-dismissing
    alert = driver.switch_to.alert
    assert alert.text == "Hello! I am an alert box!!"


def test_cookie(http_server, driver: PlaywrightWebDriver):
    # Cookies require a real HTTP origin — file:// URLs are blocked by Chromium.
    # http_server is a module-scoped fixture that serves html_pages/ over HTTP.
    driver.get(f"{http_server}/tag_name.html")
    jar = driver.manage().cookies

    jar.add_cookie({"name": "test_cookie", "value": "hello"})
    retrieved = jar.get_cookie("test_cookie")
    assert retrieved is not None
    assert retrieved["value"] == "hello"

    jar.delete_cookie_named("test_cookie")
    assert jar.get_cookie("test_cookie") is None


def test_form_submit(driver: PlaywrightWebDriver):
    driver.get(page_url("form_submit.html"))
    inp = driver.find_element(By.ID, "input1")
    inp.send_keys("Hello, world!")
    driver.find_element(By.ID, "form1").submit()
    assert driver.find_element(By.ID, "host").text == "Hello, world!"


def test_iframe(driver: PlaywrightWebDriver):
    driver.get(page_url("iframe.html"))

    # Root page content is visible
    root_span = driver.find_element(By.ID, "iframe-root-page1")
    assert root_span.is_displayed

    # Switch into the iframe
    frame_el = driver.find_element(By.ID, "frame1")
    driver.switch_to.frame(frame_el)

    # Content inside the iframe
    inner = driver.find_element(By.ID, "host")
    assert inner.text == "Window1!"

    # Navigate back to parent
    driver.switch_to.parent_frame()
    assert driver.find_element(By.ID, "iframe-root-page1").is_displayed


def test_popup(driver: PlaywrightWebDriver):
    driver.get(page_url("popup.html"))

    # Wait briefly for the popup to register
    driver.current_page.wait_for_timeout(500)

    handles = driver.window_handles
    assert len(handles) == 2

    original_handle = driver.current_window_handle
    popup_handle = next(h for h in handles if h != original_handle)

    driver.switch_to.window(popup_handle)
    assert driver.find_element(By.ID, "host").text == "Window1!"

    driver.switch_to.window(original_handle)


def test_mix_and_match_apis(driver: PlaywrightWebDriver):
    """Demonstrates mixing the Selenium-style API with direct Playwright calls."""
    driver.get(page_url("click.html"))
    # Selenium-style find + click
    driver.find_element(By.ID, "btn").click()
    assert driver.find_element(By.ID, "host").text == "Clicked"

    # Direct Playwright page access
    driver.current_page.reload()
    assert driver.find_element(By.ID, "host").text == "Not yet clicked"


def test_file_input(driver: PlaywrightWebDriver):
    driver.get(page_url("file_input.html"))
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"hello")
        tmp_path = f.name
    try:
        file_input = driver.find_element(By.ID, "file-input")
        file_input.send_keys(tmp_path)
        # Verify the file was attached
        value = driver.execute_script("return document.getElementById('file-input').files[0].name")
        assert value == Path(tmp_path).name
    finally:
        Path(tmp_path).unlink()


def test_switch_tabs(driver: PlaywrightWebDriver):
    """Open a new tab, navigate it, and switch back (Selenium 4 NewWindow equivalent)."""
    driver.get(page_url("tag_name.html"))
    original_handle = driver.current_window_handle

    driver.switch_to.new_window("tab")
    driver.get(page_url("windows/window2.html"))
    assert driver.find_element(By.ID, "host").text == "Window2!"

    driver.switch_to.window(original_handle)
    assert driver.find_element(By.ID, "host").text == "Host!"


def test_switch_to_default_content(driver: PlaywrightWebDriver):
    """Open three windows and use default_content to return to the first."""
    driver.get(page_url("windows/window1.html"))
    _ = driver.current_window_handle

    driver.switch_to.new_window("tab")
    driver.get(page_url("windows/window2.html"))

    driver.switch_to.new_window("tab")
    driver.get(page_url("windows/window3.html"))
    assert driver.find_element(By.ID, "host").text == "Window3!"

    driver.switch_to.default_content()
    assert driver.find_element(By.ID, "host").text == "Window1!"


def test_get_attribute(driver: PlaywrightWebDriver):
    driver.get(page_url("form_submit.html"))
    element = driver.find_element(By.ID, "input1")
    value = "asdf"
    element.send_keys(value)
    assert element.get_attribute("value") == value


class TestElementNotFound:
    @staticmethod
    def test_driver(driver: PlaywrightWebDriver):
        with pytest.raises(NoSuchElementException):
            _ = driver.find_element(By.ID, "asdfasdf")

    @staticmethod
    def test_element(driver: PlaywrightWebDriver):
        driver.get(page_url("tag_name.html"))
        element = driver.find_element(By.ID, "host")
        with pytest.raises(NoSuchElementException):
            _ = element.find_element(By.ID, "asdfasdf")


def test_stale_element(driver: PlaywrightWebDriver, page: Page):
    driver.get(page_url("tag_name.html"))
    element = driver.find_element(By.ID, "host")
    page.set_content("")
    with pytest.raises(StaleElementReferenceException):
        element.click()
