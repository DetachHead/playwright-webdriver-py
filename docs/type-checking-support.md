---
weight: 3
---

# Type checking support

Selenium's support for type checkers is pretty bad. It seems to support alternate `WebDriver` implementations but not in a type-safe way. For example, they do use an [`ABC`](https://docs.python.org/3/library/abc.html) called `BaseWebDriver`, but [it's completely empty](https://github.com/SeleniumHQ/selenium/blob/a056c9f13142d9f7ed35f45b2a79291fa9652130/py/selenium/webdriver/remote/webdriver.py#L273-L294) and not used by anything, rendering it completely useless.

`playwright-webdriver-py` works around this problem by using a [`TYPE_CHECKING`](https://typing.python.org/en/latest/spec/directives.html#type-checking) block to lie to type checkers so that they treat [`PlaywrightWebDriver`](api-reference.md#playwright_webdriver.PlaywrightWebDriver), [`PlaywrightWebElement`](api-reference.md#playwright_webdriver.PlaywrightWebElement), etc. as subtypes of the real classes, even though they aren't at runtime.

!!! example

    Here is a cut-down version of what our [`PlaywrightWebDriver`](api-reference.md#playwright_webdriver.PlaywrightWebDriver) class looks like:

    ```py
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from selenium.webdriver.remote.webdriver import WebDriver

        _BaseWebDriver = WebDriver
    else:
        _BaseWebDriver = object


    class PlaywrightWebDriver(_BaseWebDriver): ...
    ```

This has the following benefits:

- enforces that our re-implementations of the API are compatible with the real ones
- prevents type errors when using `playwright-web-driver` along with other code that was not written with support for custom `WebDriver` implementations in mind
- avoids the runtime dependency on the real `WebDriver` and associated risk of unintentionally falling back to the real `WebDriver` in cases where our re-implementation may be incomplete

??? question "Which type checker should I use?"

    I recommend using one of these:

    - [basedpyright](https://basedpyright.com/) (maintained by me)
    - [pyrefly](https://pyrefly.org/)
    - [ty](https://github.com/astral-sh/ty) (still WIP, missing some essential features)

    For an in-depth comparison between the type checkers, [see this site](https://detachhead.github.io/python-type-checker-comparison/) (also maintained by me, but I try to be as unbiased as possible)
