# Usage

 <!-- You should read the docs using Mkdocs, not this file! -->

## A quick note about environment variables

The exemples showcase various environment variable settings with the
`with_env("LOGGIA_ENV_VARIABLE", "value")`. You are of course not
encouraged to modify the environment at runtime, and instead to use
the usual mechanisms, like `.env` files, CI variables, shell initialization
files, Kubernetes settings or what have you.


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
You can configure it using environment variables.

## Use with Loguru

!!! note
    You do not have to use Loguru --- but if you already adopted it, Loggia will
    configure it to interop with Python's standard logging library.

This library will automatically add to new log levels to match Loguru configuration:

- `TRACE` (level 5)
- `SUCCESS` (level 25)

```python
...
{%
    include "../tests/test_usage_docs/test_usage_with_loguru.py"
    start="# <!-- DOC:START -->"
    end="# <!-- DOC:END -->"
    dedent=true
%}
```

You can opt out of this interop through the [capture_loguru][loggia.conf.LoggerConfiguration.set_loguru_capture] setting.

!!! warning
    While we try to have the same log management for loguru and standard logging, there are some differences.
    Even in this example, you can notice the name of the loggers is different.


## Make the output pretty using the `dev` preset

```python
{%
    include "../tests/test_usage_docs/test_usage_preset_env.py"
    start="# <!-- DOC:START -->"
    end="# <!-- DOC:END -->"
    dedent=true
%}
```

See the [Presets documentation](presets.md) for more information.

## Set level to TRACE using the API

```python
{%
    include "../tests/test_usage_docs/test_usage_api_trace.py"
    start="# <!-- DOC:START -->"
    end="# <!-- DOC:END -->"
    dedent=true
%}
```

You probably want to configure the standard Python logger as well, e.g., to change the log level for some libraries.

```python
{%
    include "../tests/test_usage_docs/test_usage_custom_config.py"
    start="# <!-- DOC:START -->"
    end="# <!-- DOC:END -->"
    dedent=true
%}
```



## Configure Hypercorn or Gunicorn xSGI servers

XXX Documentation
<!--
Pass the Logger classes in your Hypercorn or Gunicorn configuration.

The logger classes are already configured for DataDog, and they support JSON structured logging for access logs.


### Hypercorn

Use [HypercornLogger][loggia.structlog_utils.hypercorn_logger.HypercornLogger] as the logger class.

### Gunicorn

Use [GunicornLogger][loggia.structlog_utils.gunicorn_logger.GunicornLogger] as the logger class. -->

## Configure the standard logger

Be careful, the handler is called default

## Using the TRACE level from the standard logger

Following the standard ManoMano log levels, and compatible with loguru,
we extended the standard logger to expose a trace level at priority 5.

You need to have the loguru capture enabled to use custom levels.


```python
...
{%
    include "../tests/test_usage_docs/test_usage_std_trace.py"
    start="# <!-- DOC:START -->"
    end="# <!-- DOC:END -->"
    dedent=true
%}
```
