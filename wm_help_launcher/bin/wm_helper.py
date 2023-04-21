#!/usr/bin/env python

"""Validate/Execute DWM keybindings defined in config.h file.

The aim of this script is twofold:
  - Validate the set of keybindings defined in config.h file for DWM.
  - Show an interactive rofi helper menu of those keybindings so that the selection gets executed.

Conventions used for the keys:
  - M: Mod/Super/Windows key (I have Super/Windows key mapped to MODKEY)
  - C: Ctrl key
  - A: Alt key
  - S: Shift key

The format of a comment line associated to a keybinding in the config.h file looks like the following:
  /*d* M+S F1 scratchpad keybindings table - toggle */

  where:
    - `/*d*` is the marker (configurable) used to indicate this is a line to be used in help output.
    - `M+S` is the combination of modifiers to be used. In this case: M (Mod, Super) + S (Shift).
    - `F1` is the key to be used.
    - `scratchpad keybindings table - toggle` is the description (useful for fuzzy-finding).

Example:

    A typical invocation could be done the following way::

    $ wm_helper.py -m key

.. moduleauthor:: robtekky <robtekky@gmail.com>

"""

import argparse
import os
import re
import sys

SHOW_SPECIAL_KEYS = False
SPECIAL_PREFIX = "XF86XK_"

# Used to identify comments including keybindings info in config.h
marker = re.compile(r"^\s*/\*d\*\s+(([MCAS](\+([MCAS]))*)|0)\s+([\w\-\+<>,\.]+)\s+(.*)\s+\*/\s*$")
invalids = re.compile(r"^\s*/\*d\*\s+([^\s]+)\s+")
fn_keys = re.compile(r"^[f, F]\d{1,2}$")
MOD_SEP = "+"
MODIFIERS = set("MCAS0+")


def _process_line(match: re.Match, line: str, keybindings_dict: dict[tuple[str, str], str]) -> None:
    # Remove separator
    list1 = match[1].split(MOD_SEP)
    set1 = set(list1)

    if len(list1) != len(set1):
        sys.exit(f"Found the following line with duplicate modifiers included:\n{line}")

    list1_ordered = sorted(list(set1))
    key2 = match[5]  # the key

    # C+A + Fi is reserved to access tty's. Check that combination is not used.
    if (set1 == {"C", "A"}) and fn_keys.match(key2):
        sys.exit(f"Found the following line using a reserved keybinding:\n{line}")

    if (k := ("".join(list1_ordered), key2)) in keybindings_dict:
        sys.exit(f"Found the following line with a duplicate keybinding:\n{line}")
    else:
        keybindings_dict[k] = match[6]


def get_keybindings_dict() -> dict[tuple[str, str], str]:
    """Get a dict containing all keybindings found in the config.h file.

    Returns:
        dict[tuple[str, str], str]: dict with all keybindings found
    """

    home = os.getenv("HOME")
    input_file = f"{home}/git/dwm/config.h"

    keybindings_dict: dict[tuple[str, str], str] = {}

    with open(input_file, "r", encoding="utf8") as file:
        for line in file:
            if _match := invalids.match(line):
                group1 = set(_match[1])
                if group1.difference(MODIFIERS) or (("0" in group1) and (len(group1) > 1)):
                    sys.exit(f"Found the following line containing invalid modifier/s:\n{line}")

            if _match := marker.match(line):
                _process_line(_match, line, keybindings_dict)

    return keybindings_dict


def translate_modifiers(key: str, _modifiers: str) -> str:
    """Translate a combination of key plus modifiers into descriptive names.

    Args:
        key (str): the key used in the keybinding
        _modifiers (str): the short version of modifiers used in the keybinding to be translated

    Returns:
        str: translation of keys combination
    """

    tr_dict = {
        "M": "Super",
        "C": "Control",
        "A": "Alt",
        "S": "Shift",
    }

    if _modifiers == "0":
        return key

    tr_mods = "+".join([tr_dict[i] for i in _modifiers])
    # Better for visibility in menu to have the key as the first field shown
    return f"{key}+{tr_mods}"


def main(mode: str) -> None:
    kb_dict = get_keybindings_dict()

    if mode == "validation":
        print(f"✅ Validation of {len(kb_dict)} keybindings in config.h succeeded!!!")
    else:
        # mode == "key", key-based output:
        # Return as many lines as entries in the dict with the fields concatenated in this order:
        #   - key
        #   - modifiers
        #   - description
        # The key and modifiers will be concatenated using '+', and the description will come after a space character.
        for (_modifiers, _key), description in kb_dict.items():
            # Do not show keybindings containing special keys if so configured
            if not _key.startswith(SPECIAL_PREFIX) or SHOW_SPECIAL_KEYS:
                print(f"{translate_modifiers(_key, _modifiers)} {description}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DWM help system.")
    parser.add_argument(
        "-m",
        "--mode",
        choices=["validation", "key"],
        default="validation",
        help="what to do (default: validation)",
    )
    args = parser.parse_args()

    main(args.mode)
