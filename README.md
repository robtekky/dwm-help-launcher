wm_help_launcher
================

![](https://github.com/robtekky/wm_help_launcher/blob/main/Peek%202023-03-04%2019-18.gif)

![](https://github.com/robtekky/wm_help_launcher/blob/main/Peek%202023-03-04%2019-40.gif)

*wm_help_launcher* is a [rofi](https://github.com/davatorium/rofi) menu launcher to **fuzzy-find and launch** applications associated to the keybindings you have defined for your window manager.

The key features are:

* **Easy to use and install**: there are two scripts involved: a python script and a bash shell script. Just configure properly the paths and you should be all set.
* **Intuitive**: fuzzy-finding will help you out getting to the right keybinding, either by using the key, the modifiers or the description of the command to be executed. No need to remember keybindings or using side panels anymore. A few keystrokes will get you to the desired command to be executed.
* **Bonus features**: static tables with all defined keybindings can be generated, both in plain text and also in html and exported to your browser. Use *gen-dwm-doc.sh* posix shell script for that.
* **More Bonus features**: you can use the python script to validate your keybindings are correct, and there are no duplicates,

## Requirements

- An X11 system.
- python 3.8+ (I use python 3.11, but just because it is faster)
- [rofi](https://github.com/davatorium/rofi)
- Bash shell
- A window manager. I use [DWM](https://dwm.suckless.org/), but it can be easily ported to other window managers, as long as there is a file where you can include all keybindings in the format the tool expects. You will find that the python script contains references to DWM and its *config.h* file.
- [xdotool](https://github.com/jordansissel/xdotool), which is in charge of invoking the associated command to the keybinding shown in the menu.
- [emacs](https://www.gnu.org/software/emacs/) editor with org mode enabled, if you want to export the keybindings table to HTML.

## Installation

- Clone the repo. Under the scripts folder, you will find the bash shell script that needs to be invoked by *rofi*, which should be something like the following:

```sh
    rofi -show keybinding -modes 'keybinding:wm_help_keybinding.sh
```


As an example, this is the configuration of the keybinding that I have on my own DWM, using F1 to launch the helper menu launcher:

```c
{ 0, XK_F1, spawn, SHCMD("rofi -show keybinding -modes 'keybinding:wm_help_keybinding.sh'") },
```

- Put the bash shell script under a folder contained on your PATH env variable.
- Add the keybinding to your *config.h* file (or whatever file is used on your WM).
- Add an entry (comment) for every keybinding you have defined on your WM. Yes, this is needed, and it has to be done manually. See section [Format](#Format) to know more about what is the format to be used so that your keybindings are identified by the tool.

## Format

The format of a comment line associated to a keybinding in the *config.h* file looks like the following:

```c
  /*d* M+S F1 scratchpad keybindings table - toggle */
```

  where:
    - `/*d*` is the marker (configurable) used to indicate this is a line to be used in help output.
    - `M+S` is the combination of modifiers to be used. In this case: M (Mod, Super) + S (Shift).
    - `F1` is the key to be used.
    - `scratchpad keybindings table - toggle` is the description (useful when fuzzy-finding).
    - spaces are used to separate the fields.

Conventions used for the keys:
  - `M`: Mod/Super/Windows key (I have Super/Windows key mapped to MODKEY)
  - `C`: Ctrl key
  - `A`: Alt key
  - `S`: Shift key

## Considerations

- Extended XKeys (XF86XK_) do not work with *xdotool*. You can configure the tool to show those entries in the menu or not, but be aware they will not get executed (``SHOW_SPECIAL_KEYS`` variable in the python script).
- For some reason, `<` and `>` keys do not work well with *xdotool* as they are. So, I have had to translate them into their keycodes in the bash shell script.
- I use a Spanish keyboard, and then I have to execute ``setxkbmap -synch es`` before every keybinding invocation. If you use a US keyboard, please remove it from the bash shell script.

## Improvements

- Add unit tests.

## Similar projects

[flybinds](https://github.com/gerardet46/flybinds) is a nice project, with similar philosophy, but using a different approach.

## Meta

robtekky@gmail.com

Distributed under the MIT license. See ``LICENSE`` for more information.

