# ROADMAP

## 0.1.0 - 2023-08-21

- [x] Properly configured standard logger either in `pretty` or `structured` mode
- [x] Basic interop with `loguru`, with `loguru` piping into standard logger
- [x] First class support for Datadog standard log attributes
- [x] Preliminary concept of presets
- [x] Most of the code shown in documentation is derived from the test suite
- [x] Move Datadog-specific reencoding into a dedicated filter
- [x] Move hypercorn/gunicorn reencoding into a dedicated filter
- [x] `dev` and `prod` presets in the `main` slot
- [x] Rename internals to have legible documentation
- [x] Clean up mkdocs settings for the reference part
- [x] Write preset tests
- [X] (MM-Internal) Artifactory release

## 0.1.1 - 2023-08-22

- [X] Fix linting, typo and doc issues

## 0.1.2 - 2023-08-24

- [X] Fixed environment variable `LOGGIA_PRESETS` that was ignored if `presets` was passed to the LoggerConfiguration constructor
- [X] Improved docs, with all options documented and other minor improvements
- [X] Fixed `extra` values KVs not being shown for `pretty` mode
- [X] Allow booleans to configure bool options, instead of only truthy strings
- [X] Fixed general log level not properly parsed if passed as a non-uppercase string or a number
- [X] Trace and success level are now only supported if loguru capture is enabled, even for standard logging

## 0.1.3 - 2023-09-07

- [X] Expand supported Python version: we now support Python 3.9, 3.10 and 3.11
  - We still recommend using Python 3.11 for the best experience
- [X] Fixed errors when `loguru` is not installed
  - We now test with `loguru` and `ddtrace` installed and not installed
- [X] We now use `pdm-backend` instead of `hatchling` for packaging
- [X] Misc. documentation and quality improvements

## 0.2.0

- [ ] Load preset through FQN in `LOGGIA_PRESETS`
- [ ] Write built-in preset override tests
- [ ] Make environment variable parsing type aware and document it
- (And more! Let us know what you'd like next.)

## Later

### More ways of using Loggia

- PyPI release
- Support 3.9+ and test with tox
- `import loggia.auto` for strictly minimal boilerplate
- `python -m loggia.auto -m mypackage` for non-intrusive logger reconfiguration

### Make Loggia more delightful

- Pre-logger for errors detecting while configuring Loggia
- Provide better error messages before calling `logging.dictConfig`
- Preset auto-activation based on feature/package detection
- Provide type stubs that help language servers recognize extensions to the logger
- Document and test `__json__` on our bundled `CustomJSONEncoder`
- Right types for Python LoggerConfiguration constructor and methods (bool and int support, not just str...)
- Good story for users to test their configuration (pytest config?)
- Capture ANSI output in usage tests, render it with `ansi2html` and include it in the documentation

### Make Loggia more configurable

- Support more conditional extensions and knobs for the pretty formatter
  - Specific datetime format
  - Optionally add thread id
  - Optionally add process id
  - Provide different palettes for the pretty formatter (ACCESSIBILITY)
  - Hide some KVs from messages
  - Optionally quoted strings to distinguish between e.g. 1 and "1"
- Support more and more custom things in our bundled JSONEncoder
- Support for user-injected filters either on the general handler or on some specific logger
- Support faster JSON encoders like `msgspec`, `orjson` and `ujson` when detected
- Allow custom formatters to be loaded via fully qualified names
- Allow custom presets to be loaded via fully qualified names
- Stronger KV support globally or per-logger
  - Through a general filter
  - Strip some KVs from messages

### Make Loggia handle more concerns

- Integration with better_exceptions and rich exception display
- Interop with structlog?

### More of Python's internals exposed

- Make our `sys.excepthook` compatible with other hooks instead of basic override
- `sys.unraisablehook()` / `threading.excepthook()` support
- audit subsystem interop

### More delightful built-in presets

- AirFlow specific support
- Scrappy specific support
- `asyncio`-specific support
- First class support for Django, Celery
- DDTrace & OpenTelemetry support
- Filters for normalization on OpenTelemetry standard attributes
- Provide helpers to have request-contextualized loggers for Django and FastAPI
- Provide helpers to have command-contextualized loggers for Click
- Provide helpers to have workload-contextualized loggers for Temporal
- MORE!

### Improve Loggia's internal quality

- Auto-generate configuration docs using our decorators and a mkdocs plugin
- Move monkey patches else where into a custom LogRecordFactory and LoggerFactory
- All code shown in documentation is derived from the test suite
- Remove dependency on `pythonjsonlogger`
- Ensure all dependencies are strictly optional - Loggia should bring no dependencies at all to respect our minimalist friends' sensibilities.
- Introduce a decent exception hierarchy - no more `RuntimeError`
