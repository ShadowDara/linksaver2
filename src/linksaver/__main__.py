"""
Allows the package to be run directly with:

    python -m linksaver <command>

It simply forwards execution to cli.main(), which contains all the actual
program logic (parsing arguments, loading the config, dispatching to the
right command, ...).
"""

from .cli import main

if __name__ == "__main__":
    main()
