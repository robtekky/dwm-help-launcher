#!/usr/bin/bash

WM_HELPER="$LOCAL_SRC/wm_help_launcher/wm_help_launcher/bin/wm_helper.py"
[ -z "$1" ] && $WM_HELPER -m key && exit 0

key_and_mods=${1%% *}
key=${key_and_mods%%+*}
mods=${key_and_mods#*+}

declare -A keycodes

keycodes["less"]="94+d"
keycodes["greater"]="Shift+94+d"

keycode="${keycodes[$key]}"

if [ "$keycode" ]; then
    key=$keycode
fi

coproc (setxkbmap -synch es && xdotool key "${mods}+${key}" > /dev/null 2>&1)
