# Functions for colorizing changes made to Strings
# Taken directly from beets by Adrian Sampson:
# https://github.com/beetbox/beets

import sys
import os

from difflib import SequenceMatcher

config = {
    'ui': {
        'color': 'yes',
        'colors': {
            'text_success': 'green',
            'text_warning': 'yellow',
            'text_error': 'red',
            'text_highlight': 'red',
            'text_highlight_minor': 'lightgray',
            'action_default': 'turquoise',
            'action': 'blue',
        },
    },
}

# On Windows platforms, use colorama to support "ANSI" terminal colors.
if sys.platform == 'win32':
    try: import colorama
    except ImportError: pass
    else: colorama.init()

COLOR_ESCAPE = "\x1b["
DARK_COLORS = {
    "black": 0,
    "darkred": 1,
    "darkgreen": 2,
    "brown": 3,
    "darkyellow": 3,
    "darkblue": 4,
    "purple": 5,
    "darkmagenta": 5,
    "teal": 6,
    "darkcyan": 6,
    "lightgray": 7
}
LIGHT_COLORS = {
    "darkgray": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "fuchsia": 5,
    "magenta": 5,
    "turquoise": 6,
    "cyan": 6,
    "white": 7
}
RESET_COLOR = COLOR_ESCAPE + "39;49;00m"

# These abstract COLOR_NAMES are lazily mapped on to the actual color in COLORS
# as they are defined in the configuration files, see function: colorize
COLOR_NAMES = ['text_success', 'text_warning', 'text_error', 'text_highlight',
               'text_highlight_minor', 'action_default', 'action']
COLORS = None


def _colorize(color, text):
    """Returns a string that prints the given text in the given color
    in a terminal that is ANSI color-aware. The color must be something
    in DARK_COLORS or LIGHT_COLORS.
    """
    if color in DARK_COLORS:
        escape = COLOR_ESCAPE + "%im" % (DARK_COLORS[color] + 30)
    elif color in LIGHT_COLORS:
        escape = COLOR_ESCAPE + "%i;01m" % (LIGHT_COLORS[color] + 30)
    else:
        raise ValueError('no such color %s', color)
    return escape + text + RESET_COLOR


def colorize(color_name, text):
    """Colorize text if colored output is enabled. (Like _colorize but
    conditional.)
    """
    if not config['ui']['color'] or 'NO_COLOR' in os.environ.keys():
        return text

    global COLORS
    if not COLORS:
        COLORS = {name:
                  config['ui']['colors'][name]#.as_str()
                  for name in COLOR_NAMES}
    # In case a 3rd party plugin is still passing the actual color ('red')
    # instead of the abstract color name ('text_error')
    color = COLORS.get(color_name)
    if not color:
        log.debug('Invalid color_name: {0}', color_name)
        color = color_name
    return _colorize(color, text)


def _colordiff(a, b, highlight='text_highlight',
               minor_highlight='text_highlight_minor'):
    """Given two values, return the same pair of strings except with
    their differences highlighted in the specified color. Strings are
    highlighted intelligently to show differences; other values are
    stringified and highlighted in their entirety.
    """
    if not isinstance(a, str) \
       or not isinstance(b, str):
        # Non-strings: use ordinary equality.
        a = str(a)
        b = str(b)
        if a == b:
            return a, b
        else:
            return colorize(highlight, a), colorize(highlight, b)

    if isinstance(a, bytes) or isinstance(b, bytes):
        # A path field.
        a = util.displayable_path(a)
        b = util.displayable_path(b)

    a_out = []
    b_out = []

    matcher = SequenceMatcher(lambda x: False, a, b)
    for op, a_start, a_end, b_start, b_end in matcher.get_opcodes():
        if op == 'equal':
            # In both strings.
            a_out.append(a[a_start:a_end])
            b_out.append(b[b_start:b_end])
        elif op == 'insert':
            # Right only.
            b_out.append(colorize('text_success', b[b_start:b_end]))
        elif op == 'delete':
            # Left only.
            a_out.append(colorize(highlight, a[a_start:a_end]))
        elif op == 'replace':
            # Right and left differ. Colorise with second highlight if
            # it's just a case change.
            if a[a_start:a_end].lower() != b[b_start:b_end].lower():
                color = highlight
            else:
                color = minor_highlight
            a_out.append(colorize(color, a[a_start:a_end]))
            b_out.append(colorize('text_success', b[b_start:b_end])) # EDIT
        else:
            assert(False)

    return ''.join(a_out), ''.join(b_out)


def colordiff(a, b, highlight='text_highlight'):
    """Colorize differences between two values if color is enabled.
    (Like _colordiff but conditional.)
    """
    if config['ui']['color']:
        return _colordiff(a, b, highlight)
    else:
        return str(a), str(b)


if __name__ == '__main__':
    oldval = "2013 8th International Conference on System of Systems Engineering"
    newval = "Proc. Int. Conf. Syst. Syst. Eng."
    oldstr, newstr = colordiff(oldval, newval)
    print(f'{oldstr} -> {newstr}')
