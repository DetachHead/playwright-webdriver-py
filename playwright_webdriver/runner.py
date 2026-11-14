"""
Selenium script runner.

Executes a Selenium Python script (written against the standard selenium library)
using ``PlaywrightWebDriver`` as the browser backend — no real ChromeDriver or
browser binary installation needed.

Usage (from a Python module)::

    from playwright_webdriver.runner import run_selenium_script

    run_selenium_script("path/to/my_script.py", headless=False)

Usage (CLI)::

    python -m playwright_webdriver.runner path/to/my_script.py
    python -m playwright_webdriver.runner path/to/my_script.py --headless

How it works
------------
The runner builds a fake ``selenium.webdriver`` namespace and injects it into
the script's execution environment before calling ``exec()``.  Any call to
``webdriver.Chrome()``, ``webdriver.Firefox()``, ``webdriver.Edge()``, or
``webdriver.Remote()`` returns a ``PlaywrightWebDriver`` instance instead of
launching a real browser via WebDriver.

``WebDriverWait`` and ``expected_conditions`` are passed through from the real
selenium library unchanged — they work with any object that implements
``find_element(by, value)``, which ``PlaywrightWebDriver`` does.
"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any

from playwright_webdriver.playwright_browser_type import PlaywrightBrowserType
from playwright_webdriver.playwright_web_driver import PlaywrightWebDriver

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_selenium_script(
    script_path: str | Path, *, headless: bool = False, extra_globals: dict | None = None
) -> None:
    """
    Run a Selenium Python script using ``PlaywrightWebDriver`` as the backend.

    Parameters
    ----------
    script_path:
        Path to the ``.py`` Selenium script to execute.
    headless:
        If ``False`` (the default), the browser window is visible so you can
        watch the interactions happen.  Set to ``True`` for CI / background runs.
    extra_globals:
        Optional dict of additional names to inject into the script's namespace.
    """
    script_path = Path(script_path)
    source = script_path.read_text(encoding="utf-8")

    # We monkey-patch only the browser factory attributes on the *real*
    # selenium.webdriver module rather than replacing the whole module.
    # Replacing it would break submodule imports like
    # ``selenium.webdriver.support.ui`` and ``selenium.webdriver.common.keys``.
    import selenium.webdriver as _real_webdriver  # ruff: ignore[import-outside-top-level] TODO: what is this script... looks super wack. i dont rly wanna support it tbh
    import selenium.webdriver.chrome.service as _real_chrome_service  # ruff: ignore[import-outside-top-level]
    import selenium.webdriver.firefox.service as _real_firefox_service  # ruff: ignore[import-outside-top-level]

    launch_options = {"headless": headless}

    def _make_driver(*_args: Any, **_kwargs: Any) -> PlaywrightWebDriver:
        return PlaywrightWebDriver.create(
            browser_type=PlaywrightBrowserType.CHROMIUM, launch_options=launch_options
        )

    class _ServiceStub:
        def __init__(self, *_: Any, **__: Any) -> None: ...

    # Names to patch on the webdriver module
    driver_names = (
        "Chrome",
        "Firefox",
        "Edge",
        "Safari",
        "Remote",
        "ChromeOptions",
        "FirefoxOptions",
        "EdgeOptions",
    )
    original_attrs: dict[str, Any] = {}
    for name in driver_names:
        original_attrs[name] = getattr(_real_webdriver, name, None)
        setattr(_real_webdriver, name, _make_driver)

    # Patch Service stubs so Service() instantiation is a no-op
    orig_chrome_service = getattr(_real_chrome_service, "Service", None)
    orig_firefox_service = getattr(_real_firefox_service, "Service", None)
    _real_chrome_service.Service = _ServiceStub
    _real_firefox_service.Service = _ServiceStub

    namespace: dict[str, Any] = {"__file__": str(script_path), "__name__": "__main__"}
    if extra_globals:
        namespace.update(extra_globals)

    try:
        exec(compile(source, str(script_path), "exec"), namespace)  # ruff: ignore[exec-builtin]
    finally:
        # Restore all patched attributes
        for name, original in original_attrs.items():
            if original is None:
                with contextlib.suppress(AttributeError):
                    delattr(_real_webdriver, name)
            else:
                setattr(_real_webdriver, name, original)
        if orig_chrome_service is not None:
            _real_chrome_service.Service = orig_chrome_service
        if orig_firefox_service is not None:
            _real_firefox_service.Service = orig_firefox_service


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run a Selenium Python script using PlaywrightWebDriver"
    )
    parser.add_argument("script", help="Path to the .py Selenium script")
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="Run headless (default: headed so you can watch)",
    )
    args = parser.parse_args()

    run_selenium_script(args.script, headless=args.headless)
