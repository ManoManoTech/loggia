# ROADMAP

For a list of past changes, see [the changelog](CHANGELOG.md).

## Next release

- See [CHANGELOG.md](CHANGELOG.md)
- (And more! Let us know what you'd like next.)

## Later (or sooner)

### More ways of using Loggia

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
- Reorganize packages so that `from loggia import logger` produces a valid logger a la loguru, with implicit initialize if need be

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
- Make environment variable parsing type aware and document it
- Stronger KV support globally or per-logger
  - Through a general filter
  - Strip some KVs from messages
- Support `LOGGIA_NO_PRESETS` to explicitely bar some presets from being enabled.

### Make Loggia handle more concerns

- Integration with better_exceptions and rich exception display
- Interop with structlog?
- Hook SIGUSR1 or SIGUSR2 and dump logger status. Useful to discover live loggers
  that are possibly hidden behind the log level. Default False, turned on in Dev
  profile.

### More of Python's internals exposed

- Make our standard hooks `sys.excepthook` compatible with other hooks instead of basic override
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
- Add tests for `loaderutils`
- Add tests for the pretty formatter
- Make environment variable parsing type aware and document it
