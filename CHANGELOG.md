# CHANGELOG


## v0.1.0 (2026-08-06)

### Build System

- Add the egg-info ignore from sync-gitignore
  ([`9de6a6f`](https://github.com/datapointchris/pytermstyle/commit/9de6a6fe759dec279a2b8354a1ef6bf6b73a91ae))

Output of forge's new sync-gitignore die, which is now part of the bootstrap sequence in
  repo-structure.md. The other three entries were already here; the die found the one that was
  missed.

- Add the generated toolchain config
  ([`2b6c1c4`](https://github.com/datapointchris/pytermstyle/commit/2b6c1c4e5928ceaf4a37185950a9d6ee951ee30d))

Output of the forge dies named in repo-structure.md § Bootstrapping, run with -F pytermstyle because
  the dies are fleet-wide by default and would otherwise rewrite every active repo in the registry.
  Nothing here is hand-written: the standard [tool.*] sections and the [tool.forge] managed list
  were merged into pyproject.toml by the same sync, which is why they were left out when it was
  first written.

Two additions the sync does not make. .markdownlintignore is the one tool config it deliberately
  does not own, and semantic-release regenerates CHANGELOG.md on every release, so markdownlint
  --fix would re-normalize a file nobody wrote. .gitignore gains only .coverage, coverage.xml and
  dist/ — uv, coverage.py, pytest, ruff and mypy each write a self-ignoring .gitignore into their
  own cache directory, so the rest of the usual Python boilerplate would be dead weight.

### Chores

- Initialize the repository
  ([`8d9afbb`](https://github.com/datapointchris/pytermstyle/commit/8d9afbb448074eac9616dc223129fc706b72d4b8))

The fleet's first shared Python library, extracted from dotfiles appcore so safekeep can leave that
  repo without carrying a sys.path hack with it.

Distribution is a git dependency pinned to a release tag, moving to the private index later.
  release.yml therefore takes python-semantic-release's version job only and drops the publish job
  the sibling repos carry: the name is taken on public PyPI by an unrelated package of the same
  purpose, and new projects do not go there regardless. The tag is the artifact.

requires-python is 3.11 rather than dotfiles' 3.13 because a library floors lower than an
  application.

### Features

- Port the house palette and help grammar from appcore
  ([`7776e01`](https://github.com/datapointchris/pytermstyle/commit/7776e01fc51c108ae4a51d3410eef8148026ebc1))

The module moves verbatim; what changes is that two accidents become documented constraints, which
  is the difference between a module sitting in the repo that uses it and a library other repos
  depend on.

The help grammar keeps its buffered rows and section state in module globals. A Screen object was
  considered and rejected: every consumer is a one-shot CLI rendering a single screen, so the
  constraint never binds, and respelling every call site as screen.help_row costs the grammar the
  prose-like reading that is its whole appeal — while forking the API away from gotermstyle and
  formatting.sh, which have to keep rendering identically.

The palette still resolves at import, so NO_COLOR set afterwards has no effect. No set_color escape
  hatch was added: nothing in the consumers parses a colour flag, safekeep has none at all, and its
  tests strip ANSI with a regex rather than toggling state, so the consumer that would need one does
  not exist. The constants are interpolated directly into f-strings everywhere, so blanking them is
  the only gate that reaches those call sites.

Names are re-exported flat from __init__ to match how every call site already spells them, with the
  module still reachable for the state resets tests need. That re-export is new public surface, so
  three tests guard it — including the twelve names safekeep imports, named explicitly so a dropped
  export fails here rather than at a tool's startup.

py.typed ships the annotations, without which a consumer's type checker ignores them despite the
  Typing :: Typed classifier.
