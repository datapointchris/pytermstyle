"""House terminal style for the Python CLIs: palette, section header, help grammar.

Counterpart to ``gotermstyle`` for the Go CLIs and ``formatting.sh`` for the bash
ones. The three render the same house style, so tools written in different
languages are indistinguishable side by side on PATH.

Names are re-exported flat, because that is how every call site spells them::

    from pytermstyle import bold, cyan, help_header, help_row

The module itself stays reachable as ``from pytermstyle import formatting`` for
tests, which reset the help grammar's module-level state between screens. See
``formatting`` for the two deliberate constraints: one help screen per process,
and a palette resolved once at import.
"""

from pytermstyle.formatting import BAR
from pytermstyle.formatting import BLUE
from pytermstyle.formatting import BOLD
from pytermstyle.formatting import COLOR
from pytermstyle.formatting import COMMAND
from pytermstyle.formatting import CYAN
from pytermstyle.formatting import GREEN
from pytermstyle.formatting import MAGENTA
from pytermstyle.formatting import RED
from pytermstyle.formatting import RESET
from pytermstyle.formatting import WHITE
from pytermstyle.formatting import YELLOW
from pytermstyle.formatting import blue
from pytermstyle.formatting import bold
from pytermstyle.formatting import clip
from pytermstyle.formatting import color_enabled
from pytermstyle.formatting import cyan
from pytermstyle.formatting import green
from pytermstyle.formatting import header
from pytermstyle.formatting import help_end
from pytermstyle.formatting import help_header
from pytermstyle.formatting import help_row
from pytermstyle.formatting import help_section
from pytermstyle.formatting import help_text
from pytermstyle.formatting import help_usage
from pytermstyle.formatting import magenta
from pytermstyle.formatting import paint
from pytermstyle.formatting import red
from pytermstyle.formatting import yellow

__all__ = [
    'CYAN',
    'YELLOW',
    'GREEN',
    'RED',
    'BLUE',
    'MAGENTA',
    'WHITE',
    'COMMAND',
    'BOLD',
    'RESET',
    'BAR',
    'COLOR',
    'color_enabled',
    'paint',
    'cyan',
    'green',
    'yellow',
    'red',
    'blue',
    'magenta',
    'bold',
    'clip',
    'header',
    'help_header',
    'help_usage',
    'help_section',
    'help_row',
    'help_text',
    'help_end',
]
