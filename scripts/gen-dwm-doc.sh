#!/bin/sh

###
# * Description:
#   Generate a table (in different formats) with the keybindings used in DWM.
#   POSIX-compliant script.
#
# * Format of the input comments in config.h:
#     A configurable marker is used to identify comment lines having keybindings definition.
#     Its current value is the regex: ^\s*/\*d\*
#
# * Format of the output table:
#     The following 3 columns are used:
#       - MODIFIERS
#           Modifier/s used in the keybinding:
#             S (Shift), M (Mod), A (Alt), and combinations using '+' character, and also nothing.
#       - KEY
#           Key used in combination with the modifiers (if any).
#       - DESCRIPTION
#           Function or description of the functionality executed with the selected keybinding.
#
# * Output options:
#   - Plain table using column command. This is the fastest option.
#   - Org mode table using emacs editor.
#   - HTML output, opened with default browser.
#
# * Dependencies:
#   - `awk`
#   - `less`
#   - `rg` (ripgrep) --- just because it is faster than regular grep
#   - `column`
#   - `emacs` with org mode support
#
# * Potential improvements:
#   - More output options added (org mode export to PDF, to ASCII, etc)
#   - Check for potential keybinding duplicates found
#   - Establish an output precedence between modifiers, so that, for instance, M goes before C, etc
###

path='/tmp'
config_file=~/git/dwm/config.h
# Remove any previous tmp file
rm $path/dwm-keybindings-*.html 2>/dev/null
tmp_file=$(mktemp --suffix=.org ${path}/dwm-keybindings-XXXX)

marker='^\s*/\*d\*\s+'  # Used to identify comments including keybindings info in config.h
column1='MODIFIERS'
column2='KEY'
column3='DESCRIPTION'

lines=$(rg -N -e "$marker" "$config_file")

if [ "$1" = "org" ]; then
    echo "$lines" | awk -v c1="$column1" -v c2="$column2" -v c3="$column3" 'BEGIN {print "|"c1"|"c2"|"c3"|"; print "|-"} {if ($2 == 0) {$2=""}; printf "|"$2"|"$3"|"; for (i=4; i<NF-1; i++) printf $i" "; print $(NF-1) }' > "$tmp_file"

    elisp_common_pre="(progn (org-mode)(org-cycle)(setq current-prefix-arg 4)(org-ctrl-c-minus)(beginning-of-buffer)(kill-whole-line)(yank)(end-of-buffer)(yank)"
    elisp_common_post="(save-buffers-kill-terminal t))"

    if  [ "$2" = "html" ] ; then
        emacs -nw --file="$tmp_file" --eval "${elisp_common_pre}(beginning-of-buffer)(insert \"#+TITLE: DWM KeyBindings\n#+OPTIONS: author:nil toc:nil timestamp:nil html-postamble:nil date:nil ^:nil\n\n\")(org-html-export-to-html)${elisp_common_post}"

        tmp_file_base_name=$(basename "$tmp_file")
        tmp_file_no_suffix="${path}/${tmp_file_base_name%.*}"
        tmp_html_file="${tmp_file_no_suffix}.html"

        xdg-open "$tmp_html_file" 2>/dev/null

        rm "$tmp_html_file"
    else
        emacs -nw --file="$tmp_file" --eval "${elisp_common_pre}${elisp_common_post})"

        less "$tmp_file"
    fi
else
    # Default: use column to dump info
    echo "$lines" | awk 'BEGIN {print " # # "} {if ($2 == 0) {$2=""}; printf " "$2"#"$3"#"; for (i=4; i<NF-1; i++) printf $i" "; print $(NF-1)}' > "$tmp_file"

    column -s '#' -t "$tmp_file" --table-columns " $column1","$column2","$column3" | less
fi

# Clean-up original temp file created
rm "$tmp_file"
