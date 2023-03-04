"""WM keybindings made easy.

.. moduleauthor:: robtekky <robtekky@gmail.com>

"""

import tomllib

with open("pyproject.toml", "rb") as f:
    pyproject_dict = tomllib.load(f)

__version__ = pyproject_dict["tool"]["poetry"]["version"]
