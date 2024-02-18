# Changelog

For a list of planned features, see [the roadmap](ROADMAP.md).

## Unreleased

- *CHANGED* `LOGGIA_SUB_LEVEL` and [set_logger_level](loggia.conf.LoggerConfiguration.set_logger_level) now accept a lowercase strings and ints as well as uppercase strings.

## 0.3.0 - 2024-01-22

_Initial Open Source Release!_

In this release, we mostly focus on adoption blockers and seriously itchy behavior. The
goal remains to have a delightful out-of-the-box experience with little to no config
required.

- **BREAKING CHANGE** `conf.add_log_filter()` has a simpler and safer signature that
  abstracts away details from the underlying logging dictconfig implementation. You can
  now either pass an instance of something that implements a filter method, or a callable,
  both with the same `[[LogRecord], bool]` signature.
- *ADDED* Python 3.12 support and updated dependencies
- *CHANGED* Default `sys.excepthook` is now set in the `prod` preset. It previously explicitly
  required an opt-in.
- *ADDED* Support for instrumenting `sys.unraisablehook` and `threading.excepthook`. Both are
  enabled by default in the `prod` preset, similarly to `sys.excepthook`. This allows
  library users to configure the solution of their choice in development for exception
  pretty printing, and stays out of the way of IPython.
- *FIXED* Log `extra_args` containing the `%` sign are now correctly rendered in pretty mode.
- *CHANGED* Propagation shenanigans and handler demultiplication have been removed. This change
  should not impact any use-cases we're aware of. It was required by the next item.
- *ADDED* `conf.add_default_handler_filter()`, the preferred way to add a filter that applies to
  all loggers with propagation on.
- *CHANGED* Loguru reconfiguration blocker is now configurable, defaults to false (disabled),
  and is turned on in the `dev` preset.

Friendly reminder that fully intend on making breaking changes until 1.0 ships.

## 0.2.0 - 2023-09-26

In this release we stabilize and do a few breaking changes to better the quality of the lib.
We expand on the core capabilities offered by 0.1

- `LOGGIA_CAPTURE_LOGURU` now defaults to `AUTO` and will not display an
      error if loguru is not available. Setting it to `ENABLED` will display an
      error if loguru is not available. Setting it to `DISABLED` will skip
      loading and configuring loguru entirely.
- `import loggia.auto` is new syntactic sugar for the common
      `import loggia.logger; loggia.logger.initialize()`
- BREAKING CHANGE: Preset preferences are now written in `snake_case` instead
      of `fulllowercase`. This will only affect adventurous custom preset authors.
- The above two changes bring the library in line with its documentation.
- Pretty Formatter: hide extra args that are formatted (@jonathan.gallon)
- Fix loguru exception handling
- Load preset through FQN in `LOGGIA_PRESETS`
- Write built-in preset override tests

## 0.1.3 - 2023-09-07

- Default log level for `Prod` preset is now `INFO` instead of `DEBUG`
- Expand supported Python version: we now support Python 3.9, 3.10 and 3.11
  - We still recommend using Python 3.11 for the best experience
- Fixed errors when `loguru` is not installed
  - We now test with `loguru` installed and not installed
- Fixed crash when `ddtrace` is not installed
- We now use `pdm-backend` instead of `hatchling` for packaging
- Misc. documentation and quality improvements

## 0.1.2 - 2023-08-24

- Fixed environment variable `LOGGIA_PRESETS` that was ignored if `presets` was passed to the LoggerConfiguration constructor
- Improved docs, with all options documented and other minor improvements
- Fixed `extra` values KVs not being shown for `pretty` mode
- Allow booleans to configure bool options, instead of only truthy strings
- Fixed general log level not properly parsed if passed as a non-uppercase string or a number
- Trace and success level are now only supported if loguru capture is enabled, even for standard logging

## 0.1.1 - 2023-08-22

- Fix linting, typo and doc issues

## 0.1.0 - 2023-08-21

This initial release is a repackaging of ~2 years of various internal logger configurations
in various states of maintenance (disrepair?) and materializes what we believe are best
practices for Python standard logging and loguru.

- Properly configured standard logger either in `pretty` or `structured` mode
- Basic interop. with `loguru`, with `loguru` piping into standard logger
- First class support for Datadog standard log attributes
- Preliminary concept of presets
- Most of the code shown in documentation is derived from the test suite
- Move Datadog-specific reencoding into a dedicated filter
- Move hypercorn/gunicorn reencoding into a dedicated filter
- `dev` and `prod` presets in the `main` slot
- Rename internals to have legible documentation
- Clean up mkdocs settings for the reference part
- Write preset tests
- (MM-Internal) Artifactory release
