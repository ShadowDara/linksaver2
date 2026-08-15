"""
Data models
===========

This module defines every dataclass that together make up the shape of a
project's ``linksaver.json`` config file.

Keeping the models separate from the load/save logic (see config.py) makes
it much easier to see, at a glance, "what data does this program store?"
without having to scroll past file I/O code.

The overall structure of a config file looks roughly like this::

    AppConfig
    ├── links        -> list[Link]          (websites/resources with credit info)
    ├── links2       -> list[str]           (plain text entries)
    ├── links3       -> list[str]           (paths to license files, legacy)
    ├── links4       -> list[Link4]         (simple "text + date" entries)
    ├── links5       -> list[Link4]         (license files with a date)
    ├── linkspkglock -> list[PackageInfo]   (imported from package-lock.json)
    ├── linkscargolock -> list[PackageInfo] (imported from Cargo.lock)
    ├── settings     -> Settings            (small toggles, e.g. menu mode)
    └── git          -> GitData             (submodules + git-splitter config)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union


@dataclass
class Submodules:
    """
    A single git submodule that Linksaver knows how to (re-)clone.

    Attributes:
        desc: Human readable description of what this submodule is for.
        clonedir: Name of the folder the repo gets cloned into.
        dir: Directory (relative to the project root) where `git clone`
            should be executed.
        repolink: The git remote URL to clone.
        repocommit: The exact commit to check out after cloning.
        branch: Optional branch name; None means "use the default branch".
    """

    desc: str
    clonedir: str
    dir: str
    repolink: str
    repocommit: str
    branch: Optional[str] = None


@dataclass
class GitSplitterData:
    """
    Settings for the git-splitter feature (see splitter.py).

    Attributes:
        maxfilesize: Any tracked file at or above this size (in Megabytes)
            is considered "too big for git" and becomes a candidate for
            splitting into chunks.
        ignorepath: List of paths (relative to the repo root) that should
            never be reported/split, even if they are large.
    """

    maxfilesize: int
    ignorepath: List[str]


@dataclass
class GitData:
    """
    Container for every git-related feature of a project's config:
    submodules to clone and the git-splitter settings.
    """

    submodules: List[Submodules] = field(default_factory=list)
    splitter: GitSplitterData = field(
        default_factory=lambda: GitSplitterData(
            maxfilesize=99,
            ignorepath=[],
        )
    )


@dataclass
class Settings:
    """
    Small user-facing toggles for how the CLI behaves.

    Attributes:
        selectmenu: When True, running the program with no/only a config
            present shows an interactive selection menu instead of
            requiring a CLI argument.
    """

    selectmenu: bool


@dataclass
class Link:
    """
    A single "full" link entry - a website, resource, or asset that should
    be credited, together with optional license/author information.
    """

    link: str
    description: str
    name: Optional[str] = None
    license: Optional[str] = None
    author: Optional[str] = None
    licenselink: Optional[str] = None
    showinlist: bool = True
    changenotice: bool = False
    date: Optional[str] = None


@dataclass
class PackageInfo:
    """
    License/credit info for a single dependency, imported either from an
    npm `package-lock.json` or a Rust `Cargo.lock` file.
    """

    name: str
    link: str
    version: str
    date: str
    license: Optional[Union[str, List[str]]] = None


@dataclass
class Link4:
    """
    A lightweight entry consisting only of some text/path and a date.

    Used both for plain text credit entries (``links4``) and for license
    files that should be dumped into the output (``links5``).
    """

    link: str
    date: str


@dataclass
class AppConfig:
    """
    The complete, in-memory representation of a project's
    ``linksaver.json`` file. This is the object that gets passed around
    to almost every command function in commands/.
    """

    projectname: str
    pretty: bool = True

    # Path/URL to the JSON schema used for editor autocompletion.
    schema: Optional[str] = None

    links: List[Link] = field(default_factory=list)
    links2: List[str] = field(default_factory=list)
    links3: List[str] = field(default_factory=list)
    links4: List[Link4] = field(default_factory=list)
    links5: List[Link4] = field(default_factory=list)

    linkspkglock: List[PackageInfo] = field(default_factory=list)
    linkscargolock: List[PackageInfo] = field(default_factory=list)

    settings: Optional[Settings] = None

    git: Optional[GitData] = None

    note: Optional[str] = None


# Backwards-compatible alias: the git-splitter settings dataclass used to
# be called `gitsplitterdata` (lowercase) and lived inside splitter.py.
# splitter.py keeps exposing that old name so any external code importing
# it still works.
gitsplitterdata = GitSplitterData
