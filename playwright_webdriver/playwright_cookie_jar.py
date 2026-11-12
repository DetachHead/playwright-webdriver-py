from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from .playwright_web_driver import PlaywrightWebDriver


class PlaywrightCookieJar:
    """Port of ``PlaywrightCookieJar : ICookieJar``."""

    def __init__(self, driver: "PlaywrightWebDriver") -> None:
        self._driver = driver

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_cookie(self, cookie_dict: dict) -> None:
        self._driver.context.add_cookies([self._to_playwright_cookie(cookie_dict)])

    def get_cookie(self, name: str) -> dict | None:
        return next((c for c in self.get_cookies() if c["name"] == name), None)

    def delete_cookie(self, cookie: dict | str) -> None:
        name = cookie if isinstance(cookie, str) else cookie["name"]
        self.delete_cookie_named(name)

    def delete_cookie_named(self, name: str) -> None:
        all_cookies = self.get_cookies()
        self._driver.context.clear_cookies()
        for c in all_cookies:
            if c["name"] != name:
                self.add_cookie(c)

    def delete_all_cookies(self) -> None:
        self._driver.context.clear_cookies()

    def get_cookies(self) -> list[dict]:
        raw = self._driver.current_page.context.cookies()
        return [self._from_playwright_cookie(c) for c in raw]

    # ------------------------------------------------------------------
    # Cookie model conversion
    # ------------------------------------------------------------------

    def _to_playwright_cookie(self, cookie: dict) -> dict:
        current_url = self._driver.current_url
        parsed = urlparse(current_url)
        domain = cookie.get("domain") or parsed.hostname

        result: dict = {
            "name": cookie["name"],
            "value": cookie["value"],
            "secure": bool(cookie.get("secure", False)),
            "httpOnly": bool(cookie.get("httpOnly", False)),
        }

        # Playwright requires either url OR domain+path.  For file:// pages
        # (or when no domain is derivable) fall back to passing the full URL.
        if domain:
            result["domain"] = domain
            result["path"] = cookie.get("path") or parsed.path or "/"
        else:
            result["url"] = current_url

        expiry = cookie.get("expiry")
        if expiry is not None:
            result["expires"] = float(expiry)

        same_site = cookie.get("sameSite")
        if same_site:
            result["sameSite"] = same_site

        return result

    @staticmethod
    def _from_playwright_cookie(cookie: dict) -> dict:
        result: dict = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie.get("domain", ""),
            "path": cookie.get("path", "/"),
            "secure": bool(cookie.get("secure", False)),
            "httpOnly": bool(cookie.get("httpOnly", False)),
        }

        expires = cookie.get("expires")
        if expires and expires > 0:
            result["expiry"] = int(expires)

        same_site = cookie.get("sameSite")
        if same_site:
            result["sameSite"] = same_site

        return result
