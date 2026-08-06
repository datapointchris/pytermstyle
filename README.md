# pytermstyle

House terminal style for Python CLIs: a fixed palette, a section header, and a help-screen grammar.

Three languages render this same style. `formatting.sh` covers the bash tools, `gotermstyle` covers
the Go ones, and this covers the Python ones. Keeping them identical is the entire point — tools
written in different languages sit next to each other on `PATH`, and a user should not be able to
tell which is which from the help screen.

## The help grammar

Help output is described rather than formatted. No call site passes a width, a color, or a padding
count:

```python
from pytermstyle import help_end, help_header, help_row, help_section, help_usage

help_header('menu labs', 'Small experiments worth revisiting.')
help_usage('menu labs <verb>')

help_section('Commands')
help_row('menu labs list', '', 'List every lab')
help_row('menu labs show', '<id>', 'Show one lab')

help_end()
```

`help_row` buffers instead of printing, so the flush sizes the description column from the longest
row in the section. Close a screen with `help_end`. Use `help_text` rather than `print` for prose
between rows, so pending rows flush ahead of it instead of appearing below it.

Section colors are fixed for the roles that recur in every tool — Commands, Options, Examples — so
they become learnable across tools. Everything else rotates by position, which keeps adjacent
sections distinct without any screen having to choose.

There is deliberately no `dim`: it is unreadable against a large fraction of terminal themes.

## The palette

```python
from pytermstyle import bold, clip, cyan, header, red

print(f'{cyan("ready")} — {bold("3")} items')
header('Snapshots')
print(clip(some_long_path, used=12))
```

`clip` shortens text to fit the terminal alongside the columns already spoken for. Callers pass the
*uncolored* surrounding length and color the result afterwards, so a clip can never land inside an
escape sequence and leak a raw code onto the screen.

## Two deliberate constraints

**One help screen per process.** The grammar keeps buffered rows and section state in module-level
globals, so two screens rendered concurrently in one process would interleave. Every consumer is a
one-shot CLI rendering a single screen. The alternative — a `Screen` object respelled at every call
site — costs the grammar its prose-like reading and forks the API away from the bash and Go
counterparts. Tests that render several screens reset the state between them.

**The palette is resolved once, at import.** Set `NO_COLOR` or `FORCE_COLOR` *before* importing;
setting either afterwards has no effect. The constants are consumed by direct f-string
interpolation throughout every consumer, so blanking the constants is the only gate that reaches
those call sites without rewriting all of them. `NO_COLOR` (a preference) outranks `FORCE_COLOR` (a
correction to terminal detection). When nothing will render escapes, the palette resolves to empty
strings, so `<tool> --help > notes.txt` writes text.

## Installing

Stdlib-only, with no dependencies of its own — several consumers declare their whole dependency
list in a PEP 723 header, and a transitive dependency here is one they did not ask for.

Consumed as a git dependency pinned to a release tag:

```toml
[project]
dependencies = ["pytermstyle"]

[tool.uv.sources]
pytermstyle = { git = "https://github.com/datapointchris/pytermstyle", tag = "v0.1.0" }
```

Or in a single-file script's inline metadata:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["pytermstyle"]
#
# [tool.uv.sources]
# pytermstyle = { git = "https://github.com/datapointchris/pytermstyle", tag = "v0.1.0" }
# ///
```

## Development

```bash
task test       # pytest
task lint       # ruff, mypy, bandit
task fix        # ruff format and autofix
```

Releases are cut by python-semantic-release from conventional commits on `main`. Nothing is tagged
by hand.
