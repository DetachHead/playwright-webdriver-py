from __future__ import annotations

from enum import Enum


class PlaywrightBrowserType(Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
