# MM Logs Python

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/) ![Python 3.11](https://img.shields.io/badge/python-3.11-blue?style=flat) [![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)

## Objective

The objective of this package is to provide a simple and standard way to configure logging in Python projects.

We try to make it as simple as possible, while still providing a good default configuration, that can be customized.

We also try to solve some commons gotchas with structured logging in Python, like:
- configuring sys.excepthook
- configuring warnings to use logging
- configuring the standard logger and loguru to use the same handlers

The package is still in alpha, and we are open to suggestions and contributions.

## Code

We try to follow the best standards. As such, the code should be as typed as possible.
When only support Python 3.11+, so we can use the latest features.

## Usage

***REMOVED***
- Read the `Usage` docs
<!-- XXX Links to docs + review docs -->


## Logging from loguru

- no trace level by default
- logger.log(level) needs an int level, not a string

XXX Rename log to logger (import logger ez)
XXX Add a check / warnings when loguru or standar dlogging is reconfigured after us!

Explicit is better than implicit: do not use sys.excepthook by default
    Check sys.excepthook with tools like sentry, datadog, loguru...
    Can we detect another sys.excepthook?
    Check [Datadog patch](https://github.com/DataDog/dd-trace-py/pull/1307/files)
    Check with ariflow, scrappy, django, click


Python logging guidelines:

- Check the common guidelines!
- Do not use custom levels in production (use the standard ones)
- If you need a trace level, its level number should be 5
- XXX Should we map non standard levels to standard ones for structured logging?
- You should use MM-utils for logging (structlog + logging)
  - You may use any other logging tool, or make a custom configuration from scratch, but you must follow the guidelines (and thus, have a structured logging)
  - Note: MM utils logger is already configured with structlog + logging, with all the required attributes for ManoMano's use of DataDog.
    - It also comes with configurations ready for Hypercorn, Gunicorn.
    - XXX It supports ddtrace
