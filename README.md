# mm_utils

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/) ![Python 3.10](https://img.shields.io/badge/python-3.10-blue?style=flat)

PDM + Hatch

## Usage

- Add to your project with XXX
- Check the mkdocs XXX


# Logging from loguru
- no trace level by default
- logger.log(level) needs an int level, not a string

XXX Rename log to logger (import logger ez)

Explicit is better than implicit: do not use sys.excepthook by default
    Check sys.excepthook with tools like sentry, datadog, loguru...
    Can we detect another sys.excepthook?
    Check https://github.com/DataDog/dd-trace-py/pull/1307/files
    Check with ariflow, scrappy, django, click


Python logging guidelines:
- CHeck the common guidelines!
- Do not use custom levels in production (use the standard ones)
- If you need a trace level, its level number should be 5
- XXX Should we map non standard levels to standard ones for structured logging?
- You should use MM-utils for logging (structlog + logging)
  - You may use any other logging tool, or make a custom configuration from scratch, but you must follow the guidelines (and thus, have a structured logging)
  - Note: MM utils logger is already configured with structlog + logging, with all the required attributes for ManoMano's use of DataDog.
    - It also comes with configurations ready for Hypercorn, Gunicorn.
    - XXX It supports ddtrace
