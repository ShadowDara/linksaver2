# Config Code

from __future__ import annotations
import time
import json
import os
import platform
import sys
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Union
import subprocess
from . import splitter


@dataclass
class Submodules:
    """
    Dataclass for the Gitsubmodules clone data
    """

    desc: str
    clonedir: str
    dir: str
    repolink: str
    repocommit: str
    branch: Optional[str] = None


@dataclass
class GitData:
    """
    Dataclass for data for options
    """

    submodules: List[Submodules] = field(default_factory=list)
    splitter: splitter.gitsplitterdata = field(
        default_factory=lambda: splitter.gitsplitterdata(
            maxfilesize=99,
            ignorepath=[]
        )
    )


@dataclass
class Settings:
    """
    Settings Class for the program
    """

    selectmenu: bool


@dataclass
class Link:
    """
    Link Class to save a standard Link
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
    Dataclass for NPM or cargo package
    """

    name: str
    link: str
    version: str
    date: str
    license: Optional[Union[str, List[str]]] = None


@dataclass
class Link4:
    """
    Dataclass for a Sketchfab Link
    """

    link: str
    date: str


@dataclass
class AppConfig:
    """
    The AppConfig for the l2 program
    """

    projectname: str
    pretty: bool = True

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


# ---------- CONSTANTS ----------

NOTE = (
    "This file was generated with linksaver by Shadowdara for the samengine project. see https://shadowara.github.io/docs#/linksaver or or https://github.com/shadowdara/l2 for more infos"
)

SCHEMA_URL = (
    "https://raw.githubusercontent.com/ShadowDara/l2/"
    "refs/heads/master/shema.json"
)

# ---------- PATH ----------

def configPath() -> Path:
    """
    Function to get the path to the config file
    """

    return Path.cwd() / "linksaver.json"
    # return Path.cwd() / ".samengine" / "linksaver.json"


def save(config: AppConfig):
    """
    Fcuntion to save the Appconfig

    Args:
        config (AppConfig): all the config data of the Application
    """

    file = configPath()

    file.parent.mkdir(parents=True, exist_ok=True)

    data = asdict(config)

    # schema heißt im JSON $schema
    data["$schema"] = data.pop("schema")

    if config.pretty:
        text = json.dumps(data, indent=4, ensure_ascii=False)
    else:
        text = json.dumps(data, ensure_ascii=False)

    file.write_text(text, encoding="utf8")


# ---------- CONFIG ----------

def newSettings() -> Settings:
    return Settings(
        selectmenu=False,
    )


def newConfig(name: str) -> AppConfig:
    return AppConfig(
        projectname=name,
        schema=SCHEMA_URL,
        pretty=True,
        settings=newSettings(),
        note=NOTE,
    )


def load() -> AppConfig:
    """
    function which loads the linksaver config

    Raises:
        FileNotFoundError: Config file not found
        Exception: _description_

    Returns:
        AppConfig: The config data for the programm
    """

    file = configPath()

    if not file.exists():
        raise FileNotFoundError("config not found")

    data = json.loads(file.read_text(encoding="utf8"))

    if not data.get("projectname"):
        raise Exception("projectname must be set")

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
    config.linkspkglock = data["linkspkglock"]
    config.linkscargolock = data["linkscargolock"]
    config.settings = Settings(**data["settings"])

    # <-- HIER einfügen
    if data.get("git") is None:
        data["git"] = {}

    git = data["git"]

    git_splitter = git.get("splitter", {})

    config.git = GitData(
        submodules=[
            Submodules(**x)
            for x in git.get("submodules", [])
        ],
        splitter=splitter.gitsplitterdata(
            maxfilesize=git_splitter.get("maxfilesize", 99),
            ignorepath=git_splitter.get("ignorepath", [])
        )
    )

    return config
