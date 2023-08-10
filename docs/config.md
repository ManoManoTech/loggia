# Configuring the logger

Almost all configuration can and should be passed through environment variables, to follow the [12-factor app](https://12factor.net/) principles.

## Environment variables

| Variable name(s) | From python | Default value | Description |
|------------------|---|------------|-------------|
| `LOGGIA_LEVEL` | [`set_general_level`][loggia.conf.LoggerConfiguration.set_general_level] |`INFO` | The log level number or name. |
| `LOGGIA_SUB_LEVEL` | [`set_logger_level`][loggia.conf.LoggerConfiguration.set_logger_level] |`INFO` | The log level number or name for any given named logger. |
| `LOGGIA_FORMATTER` | [`set_default_formatter`][loggia.conf.LoggerConfiguration.set_default_formatter] | `structured` | The log formatter name (`pretty` or `structured`). |
| `LOGGIA_SET_EXCEPTHOOK` | [`set_excepthook`][loggia.conf.LoggerConfiguration.set_excepthook] | `True` | Whether the logger should set the `sys.excepthook`. |
| `LOGGIA_CAPTURE_WARNINGS` | [`capture_warnings`][loggia.conf.LoggerConfiguration.set_capture_warnings] | `True` | Whether the logger should capture warnings from the `warnings` module. |
| `LOGGIA_CAPTURE_LOGURU` | [`capture_loguru`][loggia.conf.LoggerConfiguration.set_loguru_capture] | `True` | Whether the logger should capture logs emitted through loguru. |

!!! note
    For boolean values coming from the environment, most values are truthy, and a few
    values are falsy: `FALSE`, `0`, `F`, `NO` and `DISABLED` will be intepreted as `False`.

    The falsy values are case-insentive, i.e. `disabled` is also `False`.


## Configuration precedence

The configuration is loaded in the following order:

``` mermaid

stateDiagram-v2
defaults : Loggia default dictconfig
args : Python arguments
env : Environment variables
calls : Function calls


defaults --> args
args --> env
env --> calls
```


1. Base default config, from [the base dictconfig][loggia.constants.BASE_DICTCONFIG]. _You can't change this._
2. Python arguments when creating the [`LoggerConfiguration`][loggia.conf.LoggerConfiguration] / on [`initialize`][loggia.logger.initialize]
3. Environment variables
4. Function called on the LoggerConfiguration, like [`set_default_formatter`][loggia.conf.LoggerConfiguration.set_default_formatter]


## Config module

::: loggia.conf
    options:
        show_source: false
        show_signature: false
        show_signature_annotations: false
        <!-- members:
          - LoggerConfiguration
          - load_config -->
