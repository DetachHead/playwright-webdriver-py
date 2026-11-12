"""
Maps Selenium ``Keys`` unicode private-use characters to Playwright key names.

Selenium represents special keys as single unicode characters in the private-use
area (U+E000–U+F8FF).  Playwright's ``locator.press()`` / ``page.keyboard.press()``
uses string names like ``"Enter"``, ``"Tab"``, etc.
"""

# Maps every Selenium Keys constant value → Playwright key name
SELENIUM_TO_PLAYWRIGHT: dict[str, str] = {
    "\ue000": "Unidentified",
    "\ue001": "Cancel",
    "\ue002": "Help",
    "\ue003": "Backspace",
    "\ue004": "Tab",
    "\ue005": "Clear",
    "\ue006": "Enter",      # Keys.RETURN
    "\ue007": "Enter",      # Keys.ENTER
    "\ue008": "Shift",
    "\ue009": "Control",
    "\ue00a": "Alt",
    "\ue00b": "Pause",
    "\ue00c": "Escape",
    "\ue00d": " ",          # Keys.SPACE
    "\ue00e": "PageUp",
    "\ue00f": "PageDown",
    "\ue010": "End",
    "\ue011": "Home",
    "\ue012": "ArrowLeft",
    "\ue013": "ArrowUp",
    "\ue014": "ArrowRight",
    "\ue015": "ArrowDown",
    "\ue016": "Insert",
    "\ue017": "Delete",
    "\ue018": ";",
    "\ue019": "=",
    "\ue01a": "0",
    "\ue01b": "1",
    "\ue01c": "2",
    "\ue01d": "3",
    "\ue01e": "4",
    "\ue01f": "5",
    "\ue020": "6",
    "\ue021": "7",
    "\ue022": "8",
    "\ue023": "9",
    "\ue024": "*",
    "\ue025": "+",
    "\ue026": ",",
    "\ue027": "-",
    "\ue028": ".",
    "\ue029": "/",
    "\ue031": "F1",
    "\ue032": "F2",
    "\ue033": "F3",
    "\ue034": "F4",
    "\ue035": "F5",
    "\ue036": "F6",
    "\ue037": "F7",
    "\ue038": "F8",
    "\ue039": "F9",
    "\ue03a": "F10",
    "\ue03b": "F11",
    "\ue03c": "F12",
    "\ue03d": "Meta",       # Keys.COMMAND / Keys.META
    "\ue040": "ZenkakuHankaku",
    "\ue050": "Shift",
    "\ue051": "Control",
    "\ue052": "Alt",
    "\ue053": "Meta",
    "\ue054": "PageUp",
    "\ue055": "PageDown",
    "\ue056": "End",
    "\ue057": "Home",
    "\ue058": "ArrowLeft",
    "\ue059": "ArrowUp",
    "\ue05a": "ArrowRight",
    "\ue05b": "ArrowDown",
    "\ue05c": "Insert",
    "\ue05d": "Delete",
}

_SPECIAL_RANGE_START = "\ue000"
_SPECIAL_RANGE_END = "\uf8ff"


def is_special_key(char: str) -> bool:
    return len(char) == 1 and _SPECIAL_RANGE_START <= char <= _SPECIAL_RANGE_END


def to_playwright_key(selenium_key_char: str) -> str | None:
    """Return the Playwright key name for a Selenium Keys character, or None if unknown."""
    return SELENIUM_TO_PLAYWRIGHT.get(selenium_key_char)


def split_into_chunks(text: str) -> list[tuple[str, str]]:
    """
    Split a string (which may mix regular text with Selenium key chars) into
    ordered chunks of ``("text", value)`` or ``("key", playwright_key_name)``.

    Example::

        split_into_chunks("hello\ue006")
        → [("text", "hello"), ("key", "Enter")]
    """
    chunks: list[tuple[str, str]] = []
    buf = ""
    for ch in text:
        if is_special_key(ch):
            if buf:
                chunks.append(("text", buf))
                buf = ""
            pw_key = SELENIUM_TO_PLAYWRIGHT.get(ch)
            if pw_key:
                chunks.append(("key", pw_key))
            # silently skip unknown special chars
        else:
            buf += ch
    if buf:
        chunks.append(("text", buf))
    return chunks
