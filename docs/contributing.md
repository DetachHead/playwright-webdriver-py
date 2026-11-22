---
weight: 5
---

# Contributing

## AI Policy

This project does not accept any AI generated code.

Please also refrain from unnecessarily padding out your issues, comments or PR descriptions using LLMs. Though you may use AI to assist with translations if you aren't fluent in English.

If you are interested in the motivation behind this decision, [see here](https://detachhead.codeberg.page/workproperly/blog/2026/07/21/i-dont-like-ai/).

!!! note

    [The original maintainer of this project](credits.md) seems to have heavily relied on AI when developing the original version of `playwright-webdriver-py`. As a result, there were quite a few glaring issues that I've had to fix (eg. classes or methods that did not exist in the original Python selenium webdriver, needless deviations in behavior, etc.)

    While I've fixed all of the issues I encountered when using `playwright-webdriver-py` in my own project, there are probably still issues that I haven't noticed yet. None of my contributions since taking over this project have been AI assisted and no AI generated contributions will be accepted going forward.

## Local development

### Setup

We recommend using VSCode (or better yet [VSCodium](https://vscodium.com/)), as there are project configuration files in the repo that set everything up correctly (linters/formatters, etc).

1. hit <kbd>F1</kbd> > `Tasks: Run task` > `install dependencies`, or run the following command:

    ```py
    ./pw uv sync
    ```

    This will install all dependencies required for the project (uv and all the python dependencies). They are all installed locally to `./.venv` and `./.pyprojectx`.

1. Press "Yes" when prompted by VScode to install the recommended extensions and use the newly created virtualenv.

### Running Tests

```bash
./pw test
```

All tests use local HTML fixtures and an ephemeral HTTP server — no internet connection required.
