# Loggia

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/) ![Python 3.11](https://img.shields.io/badge/python-3.11-blue?style=flat) [![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/charliermarsh/ruff)

## Objective

The objective of this package is to provide a simple and standard way to configure logging in Python projects, using the standard `logging` module, and compatible with [loguru](https://loguru.readthedocs.io/en/stable/index.html).

We aim for a batteries-included, no configuration required, delightful out-of-the box experience.

The bundled configuration is opinionated and suits our purposes well, but we recognize your opinion will differ and provide various mechanisms of increasing complexity to tune logging to your liking.

Loggia is **not** a new Python logger - it's a nice way to configure - and share configuration - for Python's standard logging and as well as loguru.

!!! warning
    While this package is in an early 0.x release, it's built upon years of
    development and production usage in various projects.

    Loggia as a logging configuration bundle is young, but the configuration
    itself is what we most enjoyed working with for some time now.

## Usage

***REMOVED***
2. `from loggia.logger import initialize; initialize()` is a strong starting point
3. Read the [Usage](docs/usage.md) docs should you need to tune things.

## Features

- Delightful standard logging configuration in `pretty` or `structured` mode
- Compatibility with `loguru` (WIP) - you can keep using Loguru's API as much as you like or need it, while Loggia takes care of all the other standard-logging based loggers.
- configuring [`sys.excepthook`](https://docs.python.org/3/library/sys.html#sys.excepthook) to properly log uncaught exceptions
- using [`logging.captureWarnings`](https://docs.python.org/3/library/logging.html#logging.captureWarnings_warnings) to log warnings
- configuring the standard logger and [loguru](https://loguru.readthedocs.io/en/stable/index.html) to use the same handlers


## Code standards

This is currently a very typed Python 3.11 codebase, with a various assortments
of linters.

We plan on retrofitting support for 3.10 and possibly 3.9 i.e. we will endeavor to support either the last 3 or 4 stable Python releases.
