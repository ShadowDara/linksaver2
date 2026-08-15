"""
Linksaver
=========

A small command-line tool by Shadowdara that helps you keep track of every
link, license and third-party credit that belongs to a project (websites,
npm/cargo packages, git submodules, ...) and turns that list into a nice
Markdown or TXT file.

This file makes the folder a Python *package* so that things like

    python -m linksaver
    from linksaver import cli

work. It intentionally stays almost empty - all the real logic lives in
the other modules (config.py, cli.py, commands/, ...).
"""

from .version import ___version___ as __version__

__all__ = ["__version__"]
