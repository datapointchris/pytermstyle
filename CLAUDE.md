# pytermstyle

A stdlib-only library that gives Python CLIs one house terminal style. It holds a fixed ANSI
palette, a boxed section header, and a help-screen grammar that sizes its own columns. All of it is
`src/pytermstyle/formatting.py`, and `__init__.py` only re-exports its names flat.

## gotermstyle mirrors this by hand, and no test checks the pair

[gotermstyle](https://github.com/datapointchris/gotermstyle) is the Go rendering of the same style.
A Python tool and a Go tool sit side by side on `PATH`, and a user should not be able to tell them
apart from the help screen. gotermstyle's `color.go`, `screen.go` and `clip.go` hold a twin of each
palette code, `BAR`, the section color table and its rotation, `color_enabled`'s precedence, `clip`,
and the layout `help_section` and `flush_rows` draw. A change to any of them is a change to both
repos. No test in either repo compares their output.

The two agree on what a screen shows, not on every byte. Python opens a row's color before the
two-space indent, and Go opens it after. `test_examples_rows_use_the_command_color` pins the Python
placement. Python also writes a reset on a continuation row, which opens no color, and Go writes
none.

Both measure width in code points. Python's `len` on a `str` counts the unit Go's rune count does,
so a multibyte name aligns the same in both. Both assume a wide character, such as CJK or emoji, is
one column.

Neither library has a `dim`. It is unreadable on many terminal themes.

## The help grammar keeps its state in module globals on purpose

`help_row` buffers into `pending_rows`, and `help_section` advances `section_index`. Two screens
rendered at once in one process therefore interleave. Every consumer is a one-shot CLI rendering one
screen, so the constraint never binds. A `Screen` object was considered and rejected. Respelling
every call site as `screen.help_row` costs the grammar its prose-like reading. It also forks the API
from the bash helper library this mirrors function for function. gotermstyle keeps the same state on
a `Screen`, because Go runs its tests in one process and its programs concurrently.

## The public contract is wider than `__all__`

- **Every name in `__all__`, imported flat.** A dropped name fails a consumer at import, before any
  call site runs. `test_the_names_a_consuming_cli_imports_are_all_exported` lists one consuming
  CLI's imports by hand, so dropping one fails here first.
- **`pytermstyle.formatting` and its globals `pending_rows`, `section_title` and `section_index`.**
  A consumer's tests reset them between screens. Renaming one breaks those tests with `__all__`
  unchanged.
- **The palette constants are plain strings, fixed at import.** Consumers interpolate them straight
  into f-strings. Blanking the constants is the only color gate that reaches those call sites, so a
  lazy or callable palette changes every one of them. `NO_COLOR` or `FORCE_COLOR` set after import
  has no effect.
- **No dependencies, and a low Python floor.** A consumer that is a single-file script declares its
  whole dependency list in a PEP 723 header. A dependency added here is one it never asked for.
  Raising `requires-python` excludes a consumer on an older Python. `.python-version` holds the
  floor, so a local run tests it.

## Without forced color the tests pass vacuously

pytest captures stdout with an object that is not a terminal, so the palette resolves to empty
strings. `tests/conftest.py` sets `FORCE_COLOR` before any test module imports pytermstyle. Without
it, `row.startswith(formatting.CYAN)` is true of every string.

- Every grammar test calls `reset_help_state()` first. The module globals carry from one test into
  the next.
- A test of the colorless palette reloads `formatting` under `NO_COLOR`, through
  `reloaded_without_color`. It reloads again on the way out, through `restore_color`.
- Such a test asserts through the reloaded module. The flat names on the package were bound at first
  import, so `pytermstyle.CYAN` keeps its color across the reload.

## A release reaches a consumer only when it moves its pin

Consumers install from this repo's git tags. Each pins an exact tag in `[tool.uv.sources]` or a PEP
723 header, so a release changes nothing until that pin moves. The `pytermstyle` name on PyPI
belongs to an unrelated package. A consumer declaring the dependency without the git source gets
that package.

A consumer's built wheel drops its git source and names a bare `pytermstyle`. So `release.yml`'s
`publish` job uploads each release to the package index those consumers publish their wheels to,
and an install naming that index takes this package from it. It never uploads to PyPI.

python-semantic-release cuts the tag through a shared reusable workflow, after `validate.yml`
passes. A breaking change on 0.x ships as a minor. Reaching 1.0 is a deliberate edit to
`[tool.semantic_release]`, and its comments say which key. The release notes are the GitHub release
body, and no `CHANGELOG.md` is written.

## Lint and CI config is generated outside this repo

A file whose first line is a toolchain stamp comment is generated from a shared toolchain standard.
`.pre-commit-config.yaml` and `.github/workflows/validate.yml` are two. So are the `[tool.*]` keys
in pyproject.toml's `managed` record, and the `ruff` pin in the dev group. A hand edit to any of
them is reverted on the next regeneration. A `[tool.*]` key absent from that record belongs to this
project. `release.yml` is hand-written.
