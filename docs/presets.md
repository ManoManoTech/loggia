# Loggia Presets

Loggia bundles a bunch of delightful presets for many parts of the Python ecosystem.

It's actually its _raison d'etre_ : bundling configuration is arguably what differentiates
Loggia from most other loggers. We're not a logger, we're a logger distribution of sorts.

Presets can configure any part of the logger in any way possible. We do not shy away
from monkey patches when they bring valuable functionality, and we strive to have the best
configuration possible in a one size fits all spirit.

## Loaded presets

Loggia loads all the presets in [`loggia.presets`][loggia.presets] by default.

Presets that may conflict with each other are handling through "preset slots", as described
below.

!!! note
    The ROADMAP includes an item where we plan on conditionally loading presets using
    some form of feature detection.

## Preset Slots

A Loggia preset may have one or more `slots` defined. What is a `slot`?
A way to express a concern where only one preset may apply.

For instance, the `main` slot currently has a `prod` and a `dev` preset, that configure
structured and pretty output formats, respectively.

| Slot            | Available implementations                                               |
| --------------- | ----------------------------------------------------------------------- |
| `main`          | [`dev`][loggia.presets.dev] ; [`prod`][loggia.presets.prod]             |
| `normalization` | [`datadog`][loggia.presets.datadog_normalisation] ; `otel` (in ROADMAP) |

### Preset Preferences

When multiple presets are available for a given slot, something needs to decide which preset
to use. This is controlled by the `LOGGIA_PRESETS` environment variable, as well as the `presets`
argument to the [LoggerConfiguration][loggia.conf.LoggerConfiguration] constructor.

It is expected to be a comma separated string of preset names, identifying which preset wins
for each of the slots.

The default `LOGGIA_PRESETS` value is `"prod"`. This means you have to opt-in to pretty formatting
(by doing something like `export LOGGIA_PRESETS=dev`) - and loggia setups can go to production without a single setting in many instances.

Loggia will figure out which preset belongs to which slot - conflicting or confusing slot
to preset mappings are unsupported/forbidden. This could be revisited before 1.0.

## Writing and contributing presets

If you happen to reuse Loggia configuration code or have identical environment variables
accross several deployments, we recommend you try writing a preset instead.

Pending a better tutorial, look at the packages in the `loggia.presets` namespace for
inspiration. In most instances, you can cut and paste your Loggia configuration code
in an `apply` method and be done with it.

### Registering your new preset

Adding the fully qualified name of your preset (i.e. `"mypackage.mysubpackage.MyPreset"`)
to `LOGGIA_PRESETS` is enough for Loggia to load it.

Alternatively, if you are using the constructor parameter, you'll be happy to find out
it accepts a `list[str|BasePreset]` as a value.

### Overriding built-in presets

You may also opt to inherit from one of the base presets, like perhaps the `Dev` one.
This new slotted preset will be picked up automatically after setting `LOGGIA_PRESETS`.
