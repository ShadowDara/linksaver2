# Linksaver
# by Shadowdara

# This is python cli script to save your links for your projects
# Read the Docs for more Infos
# https://shadowdara.github.io/docs/#/linksaver

# licensed under Apache license 2.0 by Shadowdara 2026
# DO NOT REMOVE THIS NOTICE !!!

# pylint: disable=invalid-name

"""
Linksaver by Shadowdara
========================

This module is intentionally "thin": it only

  1. loads the config file (config.load()),
  2. figures out which command the user wants (a CLI argument, or the
     interactive menu - see commands/ui.py),
  3. and dispatches to the matching function in the `commands` package.

All the actual command logic lives in commands/*.py - see that package's
__init__.py for an overview of which file does what.
"""

from __future__ import annotations

import sys
import time

from . import splitter
from .config import AppConfig, load, newConfig
from .commands import export_cmd, imports_cmd, init_cmd, links_cmd, submodules_cmd, ui


# ---------------------------------------------------------------------------
# Command dispatch table
#
# Maps the string a user types (e.g. "add", "view", "clonesubm") to the
# function that implements it. Every function here takes a single
# `AppConfig` argument. Commands that don't need the config (help/info/
# init) are handled separately in execute(), before this table is used.
# ---------------------------------------------------------------------------

COMMANDS = {
    "add": links_cmd.add,
    "add2": links_cmd.add_text,
    "add3": links_cmd.add_file,
    "view": export_cmd.view,
    "viewx": export_cmd.viewx,
    "list": links_cmd.list_links,
    "addpkg": imports_cmd.add_package_lock,
    "addcargo": imports_cmd.add_cargo_lock,
    "addsubmodule": submodules_cmd.add_git_submodule,
    "clonesubm": submodules_cmd.clone_git_submodules,
    "c": submodules_cmd.clone_git_submodules,
    "gitsplit": splitter.splitter,
    "gitrestore": splitter.restore_splitter,
    "gitview": splitter.index,
    "open": links_cmd.open_all,
    "s": lambda config: ui.status(),
}

# Commands that are handled *before* a config is required/looked at.
NO_CONFIG_COMMANDS = {"help", "-h", "--help", "h"}


# ---------- EXECUTE ----------

def execute(arg: str, config: AppConfig) -> None:
    """
    Run a single command by name.

    Args:
        arg: The command name (e.g. "add", "view", "help", ...).
        config: The already-loaded project config.
    """

    if arg in NO_CONFIG_COMMANDS:
        ui.help()
        return

    if arg == "info":
        ui.info()
        return

    if arg == "init":
        init_cmd.init()
        return

    handler = COMMANDS.get(arg)

    if handler is None:
        print("Linksaver: Argument not found!")
        return

    handler(config)


# ---------- MAIN ----------

def main() -> None:
    """
    Main entry point of the program.

    Behaviour, in order:

    1. Try to load `linksaver.json` from the current directory.
    2. If it loads and `settings.selectmenu` is on, show the interactive
       menu instead of reading `sys.argv`.
    3. Otherwise, treat `sys.argv[1]` as the command to run.
    4. If loading the config failed (e.g. it doesn't exist yet), still
       allow running `init` or `help` without a config, and otherwise
       print a friendly error explaining how to fix it.
    """

    try:
        config: AppConfig = load()

        if config.settings is not None and config.settings.selectmenu is True:
            # Interactive mode: ask the user to pick a command by number.
            arg = ui.menu()
            execute(arg, config)
            return

        if len(sys.argv) > 1:
            arg = sys.argv[1]
            execute(arg, config)
        else:
            print("Linksaver: run with one argument of help!")

    except Exception as e:
        # No valid config yet (or it's broken) - still allow `init` and
        # `help` to work so the user isn't stuck.
        if len(sys.argv) > 1:
            if sys.argv[1] == "init":
                execute("init", newConfig("temp"))
                return

            if sys.argv[1] in NO_CONFIG_COMMANDS:
                ui.help()
                return

        ui.banner()
        print("Linksaver: Config Error:", e)
        print("Run 'init' first or run with help!")

        time.sleep(2)
        sys.exit(1)


# Main stuff where everything gets executed
if __name__ == "__main__":
    main()
    sys.exit(0)
