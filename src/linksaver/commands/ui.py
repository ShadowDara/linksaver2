"""
Everything purely about *presenting* the CLI to the user:

    banner()  - the big ASCII-art "LINKSAVER" logo
    help()    - the `help` command's command list
    info()    - placeholder for a future longer "about" text
    menu()    - the interactive number-based menu (used when
                settings.selectmenu is True)
    status()  - the `s` command, a quick "git status" + oversized-files
                overview
"""

import subprocess

from .. import ansicolors
from .. import version


def banner() -> None:
    """Print the big ASCII-art LINKSAVER logo."""

    print("""
██╗     ██╗███╗   ██╗██╗  ██╗███████╗ █████╗ ██╗   ██╗███████╗██████╗
██║     ██║████╗  ██║██║ ██╔╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
██║     ██║██╔██╗ ██║█████╔╝ ███████╗███████║██║   ██║█████╗  ██████╔╝
██║     ██║██║╚██╗██║██╔═██╗ ╚════██║██╔══██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
███████╗██║██║ ╚████║██║  ██╗███████║██║  ██║ ╚████╔╝ ███████╗██║  ██║
╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝
""")


def help() -> None:
    """CLI `help`/`-h`/`--help`: print the banner + full command list."""

    banner()
    print(f"""by {ansicolors.YELLOW}shadowdara{ansicolors.END} Version {ansicolors.GREEN}{version.___version___}{ansicolors.END}

=== Commands ===

help            show this message
init            create config
add             add link
add2            add entry (text only)
add3            add license file
view            formats links into Markdown
viewx           formats links into TXT
list            list links
addpkg          add links from a package lock file
addcargo        add links from a cargo lock file
open            open all links
info            get more infos about the programm
addsubmodule    add a git submodule to the data (more infos in the docs)
clonesubm, {ansicolors.PURPLE}c{ansicolors.END}    clone the git submodules (requires git)
gitsplit        Split files in repo which are to big for git
gitrestore      restore the splitted files
gitview         View the files which are to big for git
gitrepo pack    Pack a nested .git folder into an (optionally encrypted) archive
gitrepo restore Restore a .git folder from an archive created by "gitrepo pack"
s               a little status info with gitview and git status

Run `linksaver <command> -h` for details/options of an individual command
(e.g. `linksaver gitrepo pack -h`).
""")


def info() -> None:
    """
    CLI `info`: placeholder for a longer "about/how to use" text.

    TODO: write actual content here.
    """


def menu() -> str | None:
    """
    Interactive selection menu, shown instead of requiring a CLI argument
    when `config.settings.selectmenu` is True.

    Returns:
        The command string to execute (same values as typing them on the
        CLI), or None if the user chose "Exit".
    """

    commands = [
        ("Open all links", ""),
        ("Init", "init"),
        ("Add link", "add"),
        ("Add text entry", "add2"),
        ("Add license file", "add3"),
        ("Generate Markdown", "view"),
        ("Generate TXT", "viewx"),
        ("List credits", "list"),
        ("Import package-lock.json", "addpkg"),
        ("Import Cargo.lock", "addcargo"),
        ("Help", "help"),
        ("add Git Submodule", "addsubmodule"),
        ("Clone git submodules", "clonesubm"),
        ("Split to big files for git", "gitsplit"),
        ("Restore the files which are to big", "gitrestore"),
        ("View files which are to big", "gitview"),
        ("Pack a nested .git folder (gitrepo pack)", "gitrepopack"),
        ("Restore a nested .git folder (gitrepo restore)", "gitreporestore"),
        ("Exit", None),
    ]

    print("\n=== Linksaver ===\n")

    for i, (name, _) in enumerate(commands, start=1):
        print(f"{i}. {name}")

    while True:
        try:
            choice = int(input("\nSelect: "))

            if 1 <= choice <= len(commands):
                return commands[choice - 1][1]

        except ValueError:
            pass

        print("Invalid selection.")


def status() -> None:
    """
    CLI `s`: quick overview combining `git status` with Linksaver's own
    "files too big for git" report (gitview).
    """

    subprocess.run("git status", shell=True)
    subprocess.run("l2 gitview", shell=True)
