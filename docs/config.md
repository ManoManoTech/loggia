# Configuring the logger

Almost all configuration can and should be passed through environment variables, to follow the [12-factor app](https://12factor.net/) principles.

Some settings read from multiple environments variables for convenience, like `MM_LOGS_ENV` which reads `ENV` as a fallback. If both are set, the one with the custom prefix is used.

!!! note
    For convenience, some values default change depending on the environment or the debug flag:

    - [log_formatter_name][mm_logs.settings.MMLogsConfig.log_formatter_name] will be `colored` if [env][mm_logs.settings.MMLogsConfig.env] is `dev`, and will be `structured` otherwise.
    - All `debug_*` settings will be `True` if [debug][mm_logs.settings.MMLogsConfig.debug] is `True`, and will be `False` otherwise.

## Environment variables

| Variable name(s) | Python setting | Default value | Description |
|------------------|---|------------|-------------|
| `MM_LOGS_ENV` or `ENV` | [env][mm_logs.settings.MMLogsConfig.env] | `production` | The environment name. |
| `MM_LOGS_LOG_LEVEL` or `LOG_LEVEL` | [log_level][mm_logs.settings.MMLogsConfig.log_level] |`INFO` | The log level number or name. |
| `MM_LOGS_LOG_FORMATTER_NAME` | [log_formatter_name][mm_logs.settings.MMLogsConfig.log_formatter_name] | `structured` or `colored` | The log formatter name. |
| `MM_LOGS_SET_EXCEPTHOOK` | [set_excepthook][mm_logs.settings.MMLogsConfig.set_excepthook] | `True` | Whether the logger should set the `sys.excepthook`. |
| `MM_LOGS_CAPTURE_WARNINGS` | [capture_warnings][mm_logs.settings.MMLogsConfig.capture_warnings] | `True` | Whether the logger should capture warnings from the `warnings` module. |
| `MM_LOGS_DEBUG` | [debug][mm_logs.settings.MMLogsConfig.debug] | `False` | Enable or disable all MM Logger debug options. |
| `MM_LOGS_DEBUG_SHOW_CONFIG` | [debug_show_config][mm_logs.settings.MMLogsConfig.debug_show_config] | `False` | Log the logging configuration at the end of `configure_logging()`, as DEBUG. |
| `MM_LOGS_DEBUG_JSON_INDENT` | [debug_json_indent][mm_logs.settings.MMLogsConfig.debug_json_indent] | `None` | Indent JSON logs. Should only be used for debugging. |
| `MM_LOGS_DEBUG_CHECK_DUPLICATE_PROCESSORS` | [debug_check_duplicate_processors][mm_logs.settings.MMLogsConfig.debug_check_duplicate_processors] | `False` | Run a sanity check of the structlog configuration to ensure no processors are duplicated. |
| `MM_LOGS_DEBUG_DISALLOW_LOGURU_RECONFIG` | [debug_disallow_loguru_reconfig][mm_logs.settings.MMLogsConfig.debug_disallow_loguru_reconfig] | `False` | Unused. |
| `MM_LOGS_DEBUG_SHOW_EXTRA_ARGS` | [debug_show_extra_args][mm_logs.settings.MMLogsConfig.debug_show_extra_args] | `False` | Unused. |


## Settings that can only be set in Python

| Python setting | Default value | Description |
|----------------|---------------|-------------|
| [custom_stdlib_logging_dict_config][mm_logs.settings.MMLogsConfig.custom_stdlib_logging_dict_config] | `{}` | A custom dict config for the standard library logger, to be merged with the logger default config. See [Python logging dict configuration schema]([#python-logging-configuration](https://docs.python.org/3/library/logging.config.html#dictionary-schema-details)). |

## Config module

::: mm_logs.settings
    options:
        show_source: false
        show_signature: false
        show_signature_annotations: false
        <!-- members:
          - MMLogsConfig
          - load_config -->
