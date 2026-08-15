"""
`init` command: sets up a brand-new Linksaver project in the current
directory.

Creates the `.samengine/` folder (with empty info files you can fill in
later) and a fresh `linksaver.json`, asking only for the project name.
"""

from pathlib import Path

from ..config import configPath, newConfig, save
from .prompts import prompt


def init() -> None:
    """Create `.samengine/` + a new `linksaver.json` in the current dir."""

    print("Init Linksaver")

    directory = Path.cwd() / ".samengine"
    directory.mkdir(parents=True, exist_ok=True)

    file = configPath()

    if file.exists():
        print(f"Config already exists: {file}")
        return

    # Empty placeholder "info" files that get prepended to the generated
    # Markdown/TXT output (see commands/export_cmd.py) - handy for adding
    # a project description by hand later.
    (directory / "links.info.md").write_text("", encoding="utf8")
    (directory / "links.info.txt").write_text("", encoding="utf8")

    name = prompt("Projectname: ")

    config = newConfig(name)
    save(config)

    print(f"Created config at {file}")
