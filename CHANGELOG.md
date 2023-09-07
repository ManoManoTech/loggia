# Changelog

For a list of planned features, see [the roadmap](ROADMAP.md).

## 0.1.0 - 2023-08-21

- [x] Properly configured standard logger either in `pretty` or `structured` mode
- [x] Basic interop. with `loguru`, with `loguru` piping into standard logger
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

- [X] Default log level for `Prod` preset is now `INFO` instead of `DEBUG`
- [X] Expand supported Python version: we now support Python 3.9, 3.10 and 3.11
  - We still recommend using Python 3.11 for the best experience
- [X] Fixed errors when `loguru` is not installed
  - We now test with `loguru` installed and not installed
- [X] Fixed crash when `ddtrace` is not installed
- [X] We now use `pdm-backend` instead of `hatchling` for packaging
- [X] Misc. documentation and quality improvements
