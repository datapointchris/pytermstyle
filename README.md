# pytermstyle

A stdlib-only library that gives a Python CLI a fixed terminal style. It holds an ANSI palette, a
boxed section header, and a help-screen grammar that sizes its own columns. A call site describes a
help screen row by row and never passes a width, a color or a padding count.

It is one of three renderings of one style.
[gotermstyle](https://github.com/datapointchris/gotermstyle) is the Go rendering, and a bash helper
library, `formatting.sh`, is the third. CLIs written in the three languages sit side by side on
`PATH`, and a user should not be able to tell them apart from the help screen. That is the boundary
with a general styling library. The palette is fixed and takes no theme, because a screen that chose
its own look would stand out from its neighbors.

The Python and Go renderings agree on what a screen shows, not on every byte. Python opens a row's
color before the two-space indent, and Go opens it after.

## Install

Install from a release tag in this repository. Nothing is published to PyPI, and the `pytermstyle`
name there belongs to an unrelated package. A dependency that names `pytermstyle` without the git
source installs that package instead.

```bash
# the latest release tag, to write in place of <tag>
git ls-remote --tags --refs --sort=-v:refname https://github.com/datapointchris/pytermstyle | head -1 | cut -d/ -f3

# a uv project: writes the dependency and its git source into pyproject.toml
uv add git+https://github.com/datapointchris/pytermstyle --tag <tag>

# pip reads no [tool.uv.sources], so it takes a direct reference instead
pip install "pytermstyle @ git+https://github.com/datapointchris/pytermstyle@<tag>"
```

`uv add` writes two entries. The second one keeps PyPI's package out:

```toml
[project]
dependencies = ["pytermstyle"]

[tool.uv.sources]
pytermstyle = { git = "https://github.com/datapointchris/pytermstyle", tag = "<tag>" }
```

In a single-file script, `uv add --script` writes the same dependency and git source inside its
`# /// script` block.

A release changes nothing for a consumer until its pin moves to that release's tag.

The library has no dependencies of its own. A single-file script declares its whole dependency list
in a PEP 723 header, and a dependency added here would be one it never asked for. The Python floor
is `requires-python` in `pyproject.toml`. It is held low, because raising it excludes a caller on an
older Python.

## Starting from scratch

Start with a help screen, the part the grammar exists for. Put this in `labs.py`:

```python
from pytermstyle import help_end, help_header, help_row, help_section, help_text, help_usage

help_header('labs', 'Small experiments worth revisiting.')
help_usage('labs <verb>')

help_section('Commands')
help_row('labs list', '', 'List every lab')
help_row('labs show', '<id>', 'Show one lab, with its notes')
help_row('', '', 'and the commit it was last run against')
help_text('', 'Every verb takes --json.')

help_section('Examples')
help_row('labs show 3')

help_end()
```

Then pin the library into the script and run it:

```bash
repo=https://github.com/datapointchris/pytermstyle   # where the release tags live
tag=$(git ls-remote --tags --refs --sort=-v:refname "$repo" | head -1 | cut -d/ -f3)   # the latest one
uv add --script labs.py "git+$repo" --tag "$tag"     # writes the PEP 723 header, git source included
uv run labs.py              # in a terminal: cyan bars and names, a colored rule under each section
uv run labs.py > help.txt   # into a file: the palette resolves to empty strings
cat help.txt                # the same screen as plain text, with no escape codes in it
```

`help.txt` holds this screen:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 labs
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Small experiments worth revisiting.

Usage: labs <verb>

Commands
───────────────────────
  labs list       List every lab
  labs show <id>  Show one lab, with its notes
                  and the commit it was last run against

Every verb takes --json.

Examples
───────────────────────
  labs show 3
```

The redirect is the step that proves the color gate. A screen written to a file or a pipe carries
no escapes, so `<tool> --help > notes.txt` writes readable text.
`FORCE_COLOR=1 uv run labs.py | cat -v` shows the codes a terminal would get.

## The help grammar — a screen is described, and the flush does the arithmetic

```python
help_header(name, tagline='')            # opens a screen: a blank line, the boxed name, the tagline
help_usage(*lines)                       # one or more usage lines; the Usage: label is the library's
help_section(title)                      # flushes the rows above, then prints the title and its rule
help_row(name, args='', description='')  # buffers one row; an empty name continues the row above
help_text(*lines)                        # flushes the rows above, then prints prose
help_end()                               # flushes, resets the section state, and closes the screen
```

`help_row` buffers instead of printing. The next `help_section`, `help_text` or `help_end` flushes
the buffer. The flush sizes the description column from the longest name and args in the section,
plus two spaces. Print prose between rows with `help_text` rather than `print`. A bare `print`
lands above the rows still in the buffer.

The width is measured on the uncolored text, and the color goes on afterwards, so the columns align
the same with color on or off. The width counts code points. A wide character, such as CJK or an
emoji, counts as one column, so a row carrying one pushes its description right by the extra width.

A section title that recurs across CLIs gets a fixed color, so the color becomes learnable:

- **Cyan**: Commands, Verbs, Suites, Groups, Phases.
- **Magenta**: Options, Flags, Arguments, Environment variables.
- **Yellow**: Examples.

The match ignores case. Any other title takes green, blue or white by its position on the screen,
so adjacent sections differ without any screen choosing. Rows under Examples print in the command
color, because an example is a command to type.

There is no `dim`. It is unreadable on many terminal themes.

**One help screen per process.** The grammar keeps its state in three module globals of
`pytermstyle.formatting`: `pending_rows`, `section_title` and `section_index`. Two screens rendered
at once in one process interleave. Every consumer this serves is a one-shot CLI that renders one
screen, so the constraint never binds. A `Screen` object was rejected. Respelling every call as
`screen.help_row` costs the grammar its prose-like reading. It also forks the API from
`formatting.sh`, which this mirrors function for function. gotermstyle does keep the same state on
a `Screen`, because Go runs its tests in one process and its programs concurrently.

A consumer's test that renders several screens resets those three globals between them. Their names
are part of the public contract beside `__all__`, so renaming one breaks that test with `__all__`
unchanged.

## The palette — plain strings, resolved once at import

```python
from pytermstyle import CYAN, RESET, bold, cyan, header

print(f'{cyan("ready")} — {bold("3")} items')  # a helper wraps text in a color and a reset
print(f'{CYAN}Snapshots{RESET}')                # or interpolate the constants directly
header('Snapshots')                             # a cyan bar, the title, a bar, a blank line
```

The color constants are `CYAN`, `YELLOW`, `GREEN`, `RED`, `BLUE`, `MAGENTA`, `WHITE`, `COMMAND`,
`BOLD` and `RESET`. Each helper (`cyan`, `green`, `yellow`, `red`, `blue`, `magenta`, `bold`) is
`paint(color, text)`. `BAR`, the rule `header` draws, is not a color and never blanks.

The color decision is made once, at import, in this order:

1. `NO_COLOR` set: off.
2. `FORCE_COLOR` set: on.
3. `TERM=dumb`: off.
4. Otherwise: on when stdout is a terminal.

`NO_COLOR` is a preference, and `FORCE_COLOR` corrects terminal detection, for a CI log that
renders escapes or a pager run with `-R`. Preference outranks detection. When color is off, every
color constant is the empty string.

Set `NO_COLOR` or `FORCE_COLOR` before the first import. Setting either afterwards has no effect.
Consumers interpolate the constants straight into f-strings, so blanking the constants is the only
gate that reaches those call sites. A lazy or callable palette would change every one of them.

`COLOR` holds the decision. `color_enabled(stream)` asks the same question of another stream, such
as stderr, and recolors nothing.

Under pytest, stdout is a capture object rather than a terminal, so the palette is empty and
`row.startswith(CYAN)` is true of every row. A test suite that asserts on color sets `FORCE_COLOR`
in a `conftest.py`, before anything imports pytermstyle.

## `clip` — measured before color, so it never cuts an escape

```python
print(cyan(clip(path, used=len('  ↳ '))))  # shorten to the terminal width, then color the result
```

`clip(text, used)` shortens `text` to fit the terminal beside `used` columns already spoken for, and
ends it on `…`. Callers pass the length of the uncolored text around it and color the result
afterwards. A clip therefore never lands inside an escape sequence and leaks a raw code onto the
screen. When fewer than two columns are left, `clip` returns the text whole rather than a bare
ellipsis.

The terminal width comes from `shutil.get_terminal_size`. `COLUMNS` overrides it, and a pipe falls
back to 80 columns.

## Developing it — every release is a tag cut from conventional commits

```bash
task setup    # uv sync: the virtualenv, from uv.lock
task test     # pytest
task lint     # ruff format check, ruff, mypy, bandit; writes no file
task format   # ruff format and autofix
```

python-semantic-release cuts each tag from the conventional commits on `main`, after the validate
workflow passes. Nothing is tagged by hand, and nothing is uploaded: the tag is the artifact. On 0.x
an incompatible change ships as a minor. The release notes are the GitHub release body, and no
`CHANGELOG.md` is written.

A change to the palette, `BAR`, the section colors and their rotation, the color precedence, `clip`
or the row layout is a change to gotermstyle too. No test compares the two.
