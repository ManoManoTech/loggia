# Procedural

``` python
# MM_LOGGER_LEVEL=info
def set_general_level(level: int|str) -> None:
    ...

# MM_LOGGER_FORCE_LEVEL=numba:INFO,numpy:TRACE,...
def set_logger_level(level: int|str, logger_name: str = None) -> None:
    ...

# MM_LOGGER_EXTRA_FILTERS=pkg.spkg.MonFilter,mylogname:toto.pkg.TaFilter
def add_log_filter(filter: Filter|  str, logger_name: str = None) -> None:
    ...

# MM_LOGGER_SKIP_FILTERS=pkg.spkg.MonFilter,mylogname:toto.pkg.TaFilter
def remove_log_filter(filter: Filter|  str, logger_name: str = None) -> None:
    ...

# MM_LOGGER_DEV_FORMATTER=prettyformatter|simpleformatter
def set_dev_formatter(formatter: Formatter|str) -> None:
    ...

# MM_LOGGER_PALETTE=dark256|classic16
def set_pretty_formatter_palette(palette: Palette|str) -> None:
    ...

# MM_LOGGER_JSON_ENCODER=xxx
def set_json_encoder(encoder: Type[JSONEncoder]|str) -> None:
    ...

```




- __json__ support for the builtin

# Environment


MM_LOGGER_QUIETER_TO_INFO=numpy,numpy.debug,numba...

# Data?
