"""
Commands that add entries to the config, list them, or open them:

    add()      -> CLI `add`    add a full Link entry (name/author/license/...)
    add_text() -> CLI `add2`   add a simple text-only entry
    add_file() -> CLI `add3`   add a license file reference
    list_links() -> CLI `list` print every "showable" credit to the terminal
    open_all() -> CLI `open`   open every saved link in the default browser
"""

import os
import platform
import subprocess
from datetime import datetime
from pathlib import Path

from ..config import AppConfig, save
from ..models import Link, Link4
from .prompts import prompt


# ---------- ADD A FULL LINK ----------

def add(config: AppConfig) -> None:
    """CLI `add`: interactively add a full Link entry."""

    nameInput = prompt("Name (optional): ")
    authorInput = prompt("Author (optional): ")
    licenseInput = prompt("License (optional): ")
    licenseLinkInput = prompt("License Link (optional): ")

    link = Link(
        name=nameInput if nameInput else None,
        link=prompt("New Link: "),
        description=prompt("New Description: "),
        author=authorInput if authorInput else None,
        license=licenseInput if licenseInput else None,
        licenselink=licenseLinkInput if licenseLinkInput else None,
        showinlist=prompt("Show in list? (y/n, default y): ") != "n",
        changenotice=prompt("Mark as changed? (y/n, default n): ") == "y",
        date=datetime.now().isoformat(),
    )

    config.links.append(link)
    save(config)

    print("Added new link!")


# ---------- ADD A PLAIN TEXT ENTRY (formerly "add4") ----------

def add_text(config: AppConfig) -> None:
    """CLI `add2`: add a simple text-only entry (no link metadata)."""

    entry = prompt("Entry text: ")

    link = Link4(
        link=entry,
        date=datetime.now().isoformat(),
    )

    if config.links4 is None:
        config.links4 = []

    config.links4.append(link)
    save(config)

    print("Added new entry!")


# ---------- ADD A LICENSE FILE REFERENCE (formerly "add5") ----------

def add_file(config: AppConfig) -> None:
    """CLI `add3`: reference a local license file to embed in the output."""

    filePath = prompt("License file: ")

    if not Path(filePath).resolve().exists():
        print(f"Warning: '{filePath}' does not exist.")

    link = Link4(
        link=filePath,
        date=datetime.now().isoformat(),
    )

    if config.links5 is None:
        config.links5 = []

    config.links5.append(link)
    save(config)

    print("Added license file!")


# ---------- OPEN LINKS ----------

def open_link(url: str) -> None:
    """Open a single URL/path in the OS's default handler."""

    try:
        if platform.system() == "Windows":
            os.startfile(url)
        elif platform.system() == "Darwin":
            subprocess.run(["open", url], check=False)
        else:
            subprocess.run(["xdg-open", url], check=False)
    except Exception as e:
        print("Error opening link:", e)


def open_all(config: AppConfig) -> None:
    """CLI `open`: open every saved Link entry, one by one."""

    print("Opening links...")

    for link in config.links:
        open_link(link.link)


# ---------- LIST CREDITS ----------

def list_links(config: AppConfig) -> None:
    """CLI `list`: print a human-readable credits list to the terminal."""

    print("\nCredits:\n")

    for l in config.links:
        if not l.showinlist:
            continue

        print(
            f'"{l.name or ""}" ({l.link}) '
            f'by {l.author or ""} '
            f'is licensed under {l.license or ""} '
            f'({l.licenselink or ""})'
            f'{" (changes were made)" if l.changenotice else ""}'
        )

    for entry in config.links2:
        print(entry)
