"""
Interactive wrapper around the `gitrepo` feature (see ../gitreposaver.py)
for use from the number-based menu (commands/ui.py -> menu()).

When Linksaver is run via the CLI (`linksaver gitrepo pack ...`), argparse
already builds the right `argparse.Namespace` and gitreposaver.pack()/
restore() are called directly from cli.py - see run_gitrepo() there.

The menu doesn't have CLI flags to read though, so these two functions
ask the same questions interactively and build an equivalent Namespace by
hand before calling into gitreposaver.
"""

import argparse

from .. import gitreposaver
from ..config import AppConfig
from .prompts import prompt


def pack_interactive(config: AppConfig) -> None:
    """Menu entry: pack every nested .git folder found under a root repo."""

    root = prompt("Root (Git-Repository, leer = aktuelles Verzeichnis): ") or "."
    output = prompt("Ausgabe-Verzeichnis (leer = ./git-archives): ") or "./git-archives"
    encrypt = prompt("Verschlüsseln? (y/n, default n): ") == "y"
    use_base64 = prompt("Zusätzlich Base64? (y/n, default n): ") == "y"

    args = argparse.Namespace(
        root=root,
        output=output,
        encrypt=encrypt,
        base64=use_base64,
    )

    gitreposaver.pack(args)


def restore_interactive(config: AppConfig) -> None:
    """Menu entry: restore a .git archive created by pack_interactive()."""

    archive = prompt("Archiv-Pfad: ")
    destination = prompt("Ziel-Verzeichnis: ")
    decrypt = prompt("Entschlüsseln? (y/n, default n): ") == "y"

    args = argparse.Namespace(
        archive=archive,
        destination=destination,
        decrypt=decrypt,
    )

    gitreposaver.restore(args)
