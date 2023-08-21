# Configuring the logger

Almost all configuration can and should be passed through environment variables, to follow the [12-factor app](https://12factor.net/) principles.

## Common Environment variables

| Variable name(s)   | From python                                                              | Default value | Description                                                 |
| ------------------ | ------------------------------------------------------------------------ | ------------- | ----------------------------------------------------------- |
| `LOGGIA_LEVEL`     | [`set_general_level`][loggia.conf.LoggerConfiguration.set_general_level] | `INFO`        | The log level number or name. See [log levels](/log_levels) |
| `LOGGIA_SUB_LEVEL` | [`set_logger_level`][loggia.conf.LoggerConfiguration.set_logger_level]   | `INFO`        | The log level number or name for any given named logger.    |
| `LOGGIA_PRESETS`   | [`set_logger_level`][loggia.conf.LoggerConfiguration.set_logger_level]   | `prod`        | Preferences for Loggia [Presets](/presets)                  |

## Advanced Environment variables

These variables are not commonly modified, and changing them requires a good
understanding of Loggia's internals - at least while the documentation remains
sparse.

| Variable name(s)          | From python                                                                      | Default value | Description                                                                                        |
| ------------------------- | -------------------------------------------------------------------------------- | ------------- | -------------------------------------------------------------------------------------------------- |
| `LOGGIA_FORMATTER`        | [`set_default_formatter`][loggia.conf.LoggerConfiguration.set_default_formatter] | (unset)       | The fully qualified name of a `logging.Formatter` - see `loggia.formatters` for available options. |
| `LOGGIA_SET_EXCEPTHOOK`   | [`set_excepthook`][loggia.conf.LoggerConfiguration.set_excepthook]               | `True`        | Whether the logger should set the `sys.excepthook`.                                                |
| `LOGGIA_CAPTURE_WARNINGS` | [`capture_warnings`][loggia.conf.LoggerConfiguration.set_capture_warnings]       | `True`        | Whether the logger should capture warnings from the `warnings` module.                             |
| `LOGGIA_CAPTURE_LOGURU`   | [`capture_loguru`][loggia.conf.LoggerConfiguration.set_loguru_capture]           | `True`        | Whether the logger should capture logs emitted through loguru.                                     |

## Environment variable parsers

!!! note
    For boolean values coming from the environment, most values are truthy, and a few
    values are falsy: `FALSE`, `0`, `F`, `NO` and `DISABLED` will be intepreted as `False`.

    The falsy values are case-insentive, i.e. `disabled` is also `False`.

## Configuration precedence

Loggia is configured through four different ways ([see how][loggia.conf.LoggerConfiguration]), each overriding the previous one.

``` mermaid

stateDiagram-v2
defaults : Loggia default dictconfig
presets: Presets
args : LoggerConfiguration.__init__ API
env : Environment
calls : LoggerConfiguration API


defaults --> presets
presets --> args
args --> env
env --> calls
```

 1. The [static base configuration][loggia.constants.BASE_DICTCONFIG]. NB: We go with only one handler to stdout in true cloud-native fashion.
 2. Presets are loaded according to preferences (see [Presets](/presets))
 3. Options passed to the [`LoggerConfiguration`][loggia.conf.LoggerConfiguration] constructor override the above (if any)
 4. Environment variables override the above (if any)
 5. Methods called on a [`LoggerConfiguration`][loggia.conf.LoggerConfiguration] instance in Python have the last word.
