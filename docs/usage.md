# Usage

 <!-- You should read the docs using Mkdocs, not this file! -->

## Environment variables

By default, the logger outputs JSON structured logs, and it is configured to work with DataDog.

If you want pretty logs, you can set either:

- `ENV=dev` or `MM_LOGS_ENV=dev`
- `MM_LOGS_LOG_FORMATTER_NAME=colored`

!!! warning
    This library will not load `.env` files for you.
    You are responsible for loading them yourself, using `source .env` or your favorite library.
    Possible libraries are [python-dotenv](https://pypi.org/project/python-dotenv/) or [python-decouple](https://pypi.org/project/python-decouple/) to load your `.env` files.

## Simplest usage

```python
{%
    include "../tests/test_usage_docs/test_usage_basic.py"
    start="# <!-- DOC:START -->"
    end="# <!-- DOC:END -->"
    dedent=true
%}
```

With this setup, you get a default logger, with a default configuration.
It supports JSON structured logging, and it is configured to work with DataDog.
You can configure it using environment variables. XXX LINK TO CONFIGURATION

## Custom Python logging configuration

```python
{%
    include "../tests/test_usage_docs/test_usage_custom_params.py"
    start="# <!-- DOC:START -->"
    end="# <!-- DOC:END -->"
    dedent=true
%}
```

You probably want to configure the standard Python logger as well, eg, to change the log level for some libraries.

Your custom configuration passed with [`custom_stdlib_logging_dict_config`][mm_logs.settings.MMLogsConfig.custom_stdlib_logging_dict_config] will be merged with the default one.

```python
{%
    include "../tests/test_usage_docs/test_usage_custom_config.py"
    start="# <!-- DOC:START -->"
    end="# <!-- DOC:END -->"
    dedent=true
%}
```


## Patch with Loguru

!!! note
    If your project and dependencies are not using Loguru, you can safely ignore this section.

This library will automatically add to new log levels to match Loguru configuration:

- `TRACE` (level 5)
- `SUCCESS` (level 25)

The library also provides a new function [configure_loguru][mm_logs.loguru_sink.configure_loguru] that will patch Loguru to use our logger:

You should use it if you or your dependencies use Loguru.

```python
...
{%
    include "../tests/test_usage_docs/test_usage_with_loguru.py"
    start="# <!-- DOC:START -->"
    end="# <!-- DOC:END -->"
    dedent=true
%}
```

!!! warning
    While we try to have the same log management for loguru and standard logging, there are some differences.
    Even in this example, you can notice the name of the loggers are different.


## Configure Hypercorn or Gunicorn xSGI servers

Pass the Logger classes in your Hypercorn or Gunicorn configuration.

The logger are already configured for DataDog, and they support JSON structured logging for access logs.

### Hypercorn

Use [HypercornLogger][mm_logs.structlog_utils.hypercorn_logger.HypercornLogger] as the logger class.

### Gunicorn

Use [GunicornLogger][mm_logs.structlog_utils.gunicorn_logger.GunicornLogger] as the logger class.

## Configure the standard logger

Be careful, the handler is called default
