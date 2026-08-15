# Python with ANSIColors
# by Shadowdara
#
# licensed under Apache 2.0
#
"""
A tiny collection of raw ANSI escape codes.

Usage example:

    from . import ansicolors as c
    print(f"{c.GREEN}Success!{c.END}")

Every value is just a plain string containing the escape sequence, so you
can freely concatenate them with f-strings. Always finish a colored piece
of text with END, otherwise the color "leaks" into everything printed
afterwards.
"""

# ---------- TEXT STYLES ----------

END = "\x1b[0m"           # resets all styles/colors back to default
BOLD = "\x1b[1m"

ITALIC = "\x1b[3m"
UNDERLINED = "\x1b[4m"

REVERSE_TEXT = "\x1b[7m"      # swaps foreground/background color

NOT_UNDERLINED = "\x1b[24m"
POSITIVE_TEXT = "\x1b[27m"     # undo REVERSE_TEXT

# ---------- STANDARD FOREGROUND COLORS ----------

BLACK = "\x1b[30m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
PURPLE = "\x1b[35m"
CYAN = "\x1b[36m"
WHITE = "\x1b[37m"

# ---------- STANDARD BACKGROUND COLORS ----------

BG_BLACK = "\x1b[40m"
BG_RED = "\x1b[41m"
BG_GREEN = "\x1b[42m"
BG_YELLOW = "\x1b[43m"
BG_BLUE = "\x1b[44m"
BG_PURPLE = "\x1b[45m"
BG_CYAN = "\x1b[46m"
BG_WHITE = "\x1b[47m"

# ---------- BRIGHT FOREGROUND COLORS ----------
# NOTE: some names below keep their original (slightly misspelled)
# spelling - e.g. BRIGHT_GREEM / BRIGHT_PURLPE - because other code in
# this project may already reference them under those exact names.

BRIGHT_BLACK = "\x1b[90m"
BRIGHT_RED = "\x1b[91m"
BRIGHT_GREEM = "\x1b[92m"     # bright green
BRIGHT_YELLOW = "\x1b[93m"
BRIGHT_BLUE = "\x1b[94m"
BRIGHT_PURLPE = "\x1b[95m"     # bright purple
BRIGHT_CYAN = "\x1b[96m"
BRIGHT_WHITE = "\x1b[97m"

# ---------- BRIGHT BACKGROUND COLORS ----------

BG_BRIGHT_BLACK = "\x1b[100m"
BG_BRIGHT_RED = "\x1b[101m"
BG_BRIGHT_GREEM = "\x1b[102m"   # bright green background
BG_BRIGHT_YELLOW = "\x1b[103m"
BG_BRIGHT_BLUE = "\x1b[104m"
BG_BRIGHT_PURLPE = "\x1b[105m"   # bright purple background
BG_BRIGHT_CYAN = "\x1b[106m"
BG_BRIGHT_WHITE = "\x1b[107m"
