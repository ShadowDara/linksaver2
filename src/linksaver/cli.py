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

  1. builds an argparse parser describing every command (build_parser()),
  2. loads the config file for commands that need it (config.load()),
  3. and dispatches to the matching function in the `commands` package.

All the actual command logic lives in commands/*.py - see that package's
__init__.py for an overview of which file does what.

`gitrepo` (pack/restore nested .git folders, see gitreposaver.py) is a
self-contained tool that does NOT need a linksaver.json project config -
it works on any git repository - so it's handled a little differently
from the other commands (see run_gitrepo() below).
"""

from __future__ import annotations

import argparse
import sys
import time

from . import gitreposaver, splitter, version
from .config import AppConfig, load
from .commands import export_cmd, gitrepo_cmd, imports_cmd, init_cmd, links_cmd, submodules_cmd, ui


# ---------------------------------------------------------------------------
# Command dispatch table
#
# Maps a command name to the function that implements it. Every function
# here takes a single `AppConfig` argument. Commands that don't need a
# config (help/info/init/gitrepo) are handled separately in main(),
# before this table is used.
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
    # Menu-only convenience entries for the gitrepo feature (the real CLI
    # entry point is the "gitrepo" subcommand handled by run_gitrepo()).
    "gitrepopack": gitrepo_cmd.pack_interactive,
    "gitreporestore": gitrepo_cmd.restore_interactive,
}


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """
    Build the top-level argparse parser with one subparser per command.

    Using argparse (instead of manually reading sys.argv[1]) gives us for
    free: `-h`/`--help` on every (sub-)command, argument validation,
    `--version`, and a consistent way to add commands that need their own
    flags/positional arguments (like `gitrepo pack`/`gitrepo restore`).
    """

    parser = argparse.ArgumentParser(
        prog="linksaver",
        description=(
            "Linksaver by Shadowdara - save links, licenses and credits "
            "for your project."
        ),
    )

    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"linksaver {version.___version___}",
    )

    subparsers = parser.add_subparsers(dest="command")

    # ----- simple commands: no extra arguments of their own -----

    subparsers.add_parser("help", aliases=["h"], help="show this message")
    subparsers.add_parser("info", help="get more infos about the programm")
    subparsers.add_parser("init", help="create config")
    subparsers.add_parser("add", help="add link")
    subparsers.add_parser("add2", help="add entry (text only)")
    subparsers.add_parser("add3", help="add license file")
    subparsers.add_parser("view", help="formats links into Markdown")
    subparsers.add_parser("viewx", help="formats links into TXT")
    subparsers.add_parser("list", help="list links")
    subparsers.add_parser("addpkg", help="add links from a package lock file")
    subparsers.add_parser("addcargo", help="add links from a cargo lock file")
    subparsers.add_parser("open", help="open all links")
    subparsers.add_parser(
        "addsubmodule",
        help="add a git submodule to the data (more infos in the docs)",
    )
    subparsers.add_parser(
        "clonesubm",
        aliases=["c"],
        help="clone the git submodules (requires git)",
    )
    subparsers.add_parser(
        "gitsplit", help="split files in repo which are too big for git",
    )
    subparsers.add_parser("gitrestore", help="restore the splitted files")
    subparsers.add_parser(
        "gitview", help="view the files which are too big for git",
    )
    subparsers.add_parser(
        "s", help="a little status info with gitview and git status",
    )

    # ----- gitrepo: pack/restore nested .git folders (ex-gitreposaver.py) -----

    gitrepo_parser = subparsers.add_parser(
        "gitrepo",
        help="pack/restore nested .git folders of sub-repositories",
        description=(
            "Findet Git-Repositories, die innerhalb eines anderen "
            "Git-Repositories verschachtelt sind, und kann deren .git-"
            "Verzeichnis archivieren (pack) bzw. wiederherstellen "
            "(restore). Diese Funktion benötigt KEINE linksaver.json."
        ),
    )

    gitrepo_subparsers = gitrepo_parser.add_subparsers(
        dest="gitrepo_command",
        required=True,
    )

    pack_parser = gitrepo_subparsers.add_parser(
        "pack",
        help="verschachtelte .git-Verzeichnisse archivieren",
    )
    pack_parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Main-Git-Repository (Default: aktuelles Verzeichnis).",
    )
    pack_parser.add_argument(
        "-o", "--output",
        default="./git-archives",
        help="Ausgabe-Verzeichnis (Default: ./git-archives).",
    )
    pack_parser.add_argument(
        "--encrypt",
        action="store_true",
        help="Archiv mit AES-256 verschlüsseln.",
    )
    pack_parser.add_argument(
        "--base64",
        action="store_true",
        help="Archiv zusätzlich als Base64 speichern.",
    )

    restore_parser = gitrepo_subparsers.add_parser(
        "restore",
        help="ein .git-Archiv wiederherstellen",
    )
    restore_parser.add_argument("archive", help="ZIP/ENC/B64-Archiv.")
    restore_parser.add_argument("destination", help="Ziel-Repository.")
    restore_parser.add_argument(
        "--decrypt",
        action="store_true",
        help="Archiv entschlüsseln.",
    )

    return parser


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def dispatch_simple(command: str, config: AppConfig) -> None:
    """
    Run one of the "simple" commands (the ones taking just an AppConfig)
    by name. Used both for CLI args and for the interactive menu.
    """

    handler = COMMANDS.get(command)

    if handler is None:
        print("Linksaver: Argument not found!")
        return

    handler(config)


def run_gitrepo(args: argparse.Namespace) -> None:
    """
    Handle the `gitrepo pack`/`gitrepo restore` subcommands.

    This mirrors gitreposaver.py's own error handling (it used to be a
    fully separate script) so behaviour stays identical now that it's
    reached through the main `linksaver` CLI instead.
    """

    try:
        if args.gitrepo_command == "pack":
            gitreposaver.pack(args)
        elif args.gitrepo_command == "restore":
            gitreposaver.restore(args)

    except KeyboardInterrupt:
        print("\nAbgebrochen.")
        sys.exit(130)

    except Exception as exc:
        print(f"\nFEHLER: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Main entry point of the program.

    Behaviour, in order:

    1. Parse CLI arguments with argparse.
    2. `help`/`info`/`init` never need a config - run them immediately.
    3. `gitrepo` never needs a linksaver.json either (it works on any git
       repo) - run it immediately too.
    4. For everything else, try to load `linksaver.json`.
       - If it loads and no command was given and
         `settings.selectmenu` is on, show the interactive menu.
       - If it loads and a command was given, run that command.
       - If loading fails, print a friendly error explaining how to fix
         it (run 'init' first).
    """

    parser = build_parser()
    args = parser.parse_args()

    if args.command in ("help", "h"):
        ui.help()
        return

    if args.command == "info":
        ui.info()
        return

    if args.command == "init":
        init_cmd.init()
        return

    if args.command == "gitrepo":
        run_gitrepo(args)
        return

    try:
        config: AppConfig = load()

    except Exception as e:
        ui.banner()
        print("Linksaver: Config Error:", e)
        print("Run 'init' first or run with help!")

        time.sleep(2)
        sys.exit(1)
        return

    if args.command is None:
        if config.settings is not None and config.settings.selectmenu is True:
            # Interactive mode: ask the user to pick a command by number.
            selected = ui.menu()

            if selected:
                dispatch_simple(selected, config)

            return

        print("Linksaver: run with one argument of help!")
        return

    dispatch_simple(args.command, config)


# Main stuff where everything gets executed
if __name__ == "__main__":
    main()
    sys.exit(0)
