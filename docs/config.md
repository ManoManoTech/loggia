# Configuring the logger

Almost all configuration can and should be passed through environment variables, to follow the [12-factor app](https://12factor.net/) principles.

## Environment variables

| Variable name(s) | From python | Default value | Description |
|------------------|---|------------|-------------|
| `LOGGIA_LEVEL` | [set_general_level][loggia.conf.LoggerConfiguration.set_general_level] |`INFO` | The log level number or name. |
| `LOGGIA_SUB_LEVEL` | [set_logger_level][loggia.conf.LoggerConfiguration.set_logger_level] |`INFO` | The log level number or name for any given named logger. |
| `LOGGIA_FORMATTER` | [set_default_formatter][loggia.conf.LoggerConfiguration.set_default_formatter] | `structured` | The log formatter name (`pretty` or `structured`). |
| `LOGGIA_SET_EXCEPTHOOK` | [set_excepthook][loggia.conf.LoggerConfiguration.set_excepthook] | `True` | Whether the logger should set the `sys.excepthook`. |
| `LOGGIA_CAPTURE_LOGURU` | [capture_loguru][loggia.conf.LoggerConfiguration.set_loguru_capture] | `True` | Whether the logger should capture logs emitted through loguru. |
| `LOGGIA_CAPTURE_WARNINGS` | [capture_warnings][loggia.conf.LoggerConfiguration.set_capture_warnings] | `True` | Whether the logger should capture warnings from the `warnings` module. |

!!! note
    For boolean values coming from the environment, most values are truthy, and a few
    values are falsy: `FALSE`, `0`, `F`, `NO` and `DISABLED` will be intepreted as `False`.

    The falsy values are case-insentive, i.e. `disabled` is also `False`.

## Config module

::: loggia.conf
    options:
        show_source: false
        show_signature: false
        show_signature_annotations: false
        <!-- members:
          - LoggerConfiguration
          - load_config -->
