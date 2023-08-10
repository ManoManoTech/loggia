# Configuring the logger

Almost all configuration can and should be passed through environment variables, to follow the [12-factor app](https://12factor.net/) principles.

Some settings read from multiple environments variables for convenience, like `MM_LOGS_ENV` which reads `ENV` as a fallback. If both are set, the one with the custom prefix is used.

!!! note
    For convenience, some values default change depending on the environment or the debug flag:

    - [log_formatter_name][loggia.conf.LoggerConfiguration.log_formatter_name] will be `colored` if [env][loggia.conf.LoggerConfiguration.env] is `dev`, and will be `structured` otherwise.
    - All `debug_*` settings will be `True` if [debug][loggia.conf.LoggerConfiguration.debug] is `True`, and will be `False` otherwise.

## Environment variables

| Variable name(s) | From python | Default value | Description |
|------------------|---|------------|-------------|
| `LOGGIA_LEVEL` | [set_general_level][loggia.conf.LoggerConfiguration.set_general_level] |`INFO` | The log level number or name. |
| `LOGGIA_FORMATTER` | [set_default_formatter][loggia.conf.LoggerConfiguration.set_default_formatter] | `structured` | The log formatter name (`pretty` or `structured`). |
| `LOGGIA_SET_EXCEPTHOOK` | [set_excepthook][loggia.conf.LoggerConfiguration.set_excepthook] | `True` | Whether the logger should set the `sys.excepthook`. |
| `LOGGIA_CAPTURE_LOGURU` | [capture_loguru][loggia.conf.LoggerConfiguration.capture_loguru] | `True` | Whether the logger should capture logs emitted through loguru. |
| `LOGGIA_CAPTURE_WARNINGS` | [capture_warnings][loggia.conf.LoggerConfiguration.capture_warnings] | `True` | Whether the logger should capture warnings from the `warnings` module. |

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
          - MMLogsConfig
          - load_config -->
