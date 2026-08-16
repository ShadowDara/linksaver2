"""
Config file handling
=====================

Everything related to *reading* and *writing* a project's
``linksaver.json`` file lives here. The actual data shapes (dataclasses)
live in models.py - this module only knows how to turn them into JSON and
back.

Typical usage from a command::

    from .config import load, save, newConfig

    config = load()          # raises FileNotFoundError if no config yet
    config.links.append(...)
    save(config)
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import AppConfig, GitData, GitSplitterData, Link, Link4, Settings, Submodules

# ---------- CONSTANTS ----------

# Text that gets written into every generated config file so people know
# where it came from.
NOTE = (
    "This file was generated with linksaver by Shadowdara for the "
    "samengine project. see https://shadowara.github.io/docs#/linksaver "
    "or https://github.com/shadowdara/l2 for more infos"
)

# JSON schema used by editors (e.g. VS Code) for autocompletion/validation
# of linksaver.json.
SCHEMA_URL = (
    "https://raw.githubusercontent.com/ShadowDara/l2/"
    "refs/heads/master/shema.json"
)


# ---------- PATH ----------

def configPath() -> Path:
    """
    Return the path to the config file for the *current* project.

    Linksaver always looks for/writes ``linksaver.json`` in the current
    working directory - i.e. wherever the command is run from.
    """

    return Path.cwd() / "linksaver.json"
    # return Path.cwd() / ".samengine" / "linksaver.json"


# ---------- SAVE ----------

def save(config: AppConfig) -> None:
    """
    Write an AppConfig object to disk as ``linksaver.json``.

    Args:
        config: The full config object to persist.
    """

    file = configPath()
    file.parent.mkdir(parents=True, exist_ok=True)

    data = asdict(config)

    # In Python we call the field "schema", but in the JSON file it must
    # be called "$schema" so editors recognize it as a schema reference.
    data["$schema"] = data.pop("schema")

    if config.pretty:
        text = json.dumps(data, indent=4, ensure_ascii=False)
    else:
        text = json.dumps(data, ensure_ascii=False)

    file.write_text(text, encoding="utf8")


# ---------- CREATE A FRESH CONFIG ----------

def newSettings() -> Settings:
    """Default settings used for brand-new projects."""

    return Settings(
        selectmenu=False,
    )


def newConfig(name: str) -> AppConfig:
    """
    Build a brand-new, empty AppConfig for a project called `name`.

    This does NOT write anything to disk - call save() afterwards if you
    want to persist it (see commands/init_cmd.py).
    """

    return AppConfig(
        projectname=name,
        schema=SCHEMA_URL,
        pretty=True,
        settings=newSettings(),
        note=NOTE,
    )


# ---------- LOAD ----------

def load() -> AppConfig:
    """
    Load and parse ``linksaver.json`` from the current directory.

    Missing optional sections (settings, git, links2, ...) are filled in
    with sensible defaults so that older config files created by earlier
    versions of Linksaver keep working without a manual migration step.

    Raises:
        FileNotFoundError: No linksaver.json exists in the current
            directory.
        Exception: The file exists but is missing a `projectname`.

    Returns:
        AppConfig: The fully populated config for the current project.
    """

    file = configPath()

    if not file.exists():
        raise FileNotFoundError("config not found")

    data = json.loads(file.read_text(encoding="utf8"))

    if not data.get("projectname"):
        raise Exception("projectname must be set")

    # ----- fill in defaults for anything missing (backwards compat) -----

    if "$schema" not in data:
        data["$schema"] = SCHEMA_URL

    if "settings" not in data:
        data["settings"] = asdict(newSettings())

    data.setdefault("links", [])
    data.setdefault("links2", [])
    data.setdefault("links3", [])
    data.setdefault("links4", [])
    data.setdefault("links5", [])
    data.setdefault("linkspkglock", [])
    data.setdefault("linkscargolock", [])

    # ----- build the top-level AppConfig -----

    config = AppConfig(
        projectname=data["projectname"],
        pretty=data.get("pretty", True),
        schema=data["$schema"],
        note=NOTE,
    )

    config.links = [Link(**x) for x in data["links"]]
    config.links2 = data["links2"]
    config.links3 = data["links3"]
    config.links4 = [Link4(**x) for x in data["links4"]]
    config.links5 = [Link4(**x) for x in data["links5"]]
    config.linkspkglock = [PackageInfo(**x) for x in data["linkspkglock"]]
    config.linkscargolock = [PackageInfo(**x) for x in data["linkscargolock"]]
    config.settings = Settings(**data["settings"])

    # ----- build the "git" section (submodules + splitter settings) -----

    git = data.get("git") or {}
    git_splitter = git.get("splitter", {})

    config.git = GitData(
        submodules=[
            Submodules(**x)
            for x in git.get("submodules", [])
        ],
        splitter=GitSplitterData(
            maxfilesize=git_splitter.get("maxfilesize", 99),
            ignorepath=git_splitter.get("ignorepath", []),
        ),
    )

    return config
