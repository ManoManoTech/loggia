# ROADMAP

## 0.1.0

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

## 0.2.0

- [ ] (MM-Internal) Artifactory release
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
- Support for user injected filters either on the general handler or on some specific logger
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

- Auto generate configuration docs using our decorators and an mkdocs plugin
- Move monkey patches else where into a custom LogRecordFactory and LoggerFactory
- All code shown in documentation is derived from the test suite
- Remove dependency on `pythonjsonlogger`
- Ensure all dependencies are strictly optional - Loggia should bring no dependencies at all to respect our minimalist friends' sensibilities.
- Introduce a decent exception hierarchy - no more `RuntimeError`
