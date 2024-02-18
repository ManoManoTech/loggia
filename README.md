# Loggia

[![PyPI - Version](https://img.shields.io/pypi/v/loggia)](https://pypi.org/project/loggia/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/loggia)](https://pypi.org/project/loggia/) [![PyPI - License](https://img.shields.io/pypi/l/loggia)](https://github.com/ManoManoTech/loggia/blob/main/LICENSE) [![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch) [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v0.json)](https://github.com/astral-sh/ruff)

> **The documentation is available on Github Pages**
>
> [Read it online](https://manomanotech.github.io/loggia/)

## Objective

The objective of this package is to provide a simple and standard way to configure logging in Python applications, using the standard `logging` module, and compatible with [loguru](https://loguru.readthedocs.io/en/stable/index.html).

We aim for a batteries-included, no configuration required, delightful out-of-the box experience.

The bundled configuration is opinionated and suits our purposes well, but we recognize your opinion will differ and provide various mechanisms of increasing complexity to tune logging to your liking.

Loggia is **not** a new Python logger - it's a nice way to configure - and share configuration - for Python's standard logging and as well as loguru.

!!! warning
    While this package is in an early 0.x release, it's built upon years of
    development and production usage in various projects.

    Loggia as a logging configuration bundle is young, but the configuration
    itself is what we most enjoyed working with for some time now.

## Usage

1. Add the `loggia` dependency to your project, e.g.: with PDM:
   - Directly from Pypi: `pdm add loggia`
   - With Git: `pdm add "loggia @ git+ssh://git@github.com/manomanotech/loggia.git"`
2. `#!python from loggia.logger import initialize; initialize()` is a strong starting point
   - You should call this as early as possible in your application, ideally before any other code is run, for instance by adding it in your main `__init__.py` file.
3. Read the [Usage](https://manomanotech.github.io/loggia/usage) docs should you need to tune things.

## Features

- Delightful standard logging configuration in `pretty` or `structured` mode
- Compatibility with `loguru` (WIP) - you can keep using Loguru's API as much as you like or need it, while Loggia takes care of all the other standard-logging based loggers.
- Configuring [`sys.excepthook`](https://docs.python.org/3/library/sys.html#sys.excepthook) to properly log uncaught exceptions
- Using [`logging.captureWarnings`](https://docs.python.org/3/library/logging.html#logging.captureWarnings_warnings) to log warnings
- Configuring the standard logger and [loguru](https://loguru.readthedocs.io/en/stable/index.html) to use the same handlers
- Only one non-optional dependency

## Code standards & Principles

- Lean towards being way too typed rather than untyped
- Do not depend on third-party packages (_WIP_)
- Do not crash unless explicitly asked to - fallback to sensible things, emit a warning, and move on.

## Supported versions

We currently support Python 3.9, 3.10, 3.11 and 3.12.

We may drop the support for a Python version before its end of life, to keep the codebase up to date with the latest Python features: i.e.: we will endeavor to support either the last 3 or 4 stable Python releases.

We don't plan to support earlier versions or different runtimes.
