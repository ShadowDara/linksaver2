# Linksaver
# by Shadowdara

# This is python cli script to save your links for your projects
# Read the Docs for more Infos
# https://shadowdara.github.io/docs/#/linksaver

# licensed under Appache license 2.0 by Shadowdara 2026
# DO NOT REMOVE THIS NOTICE !!!

# pylint: disable=invalid-name

"""
Linksaver by Shadowdara
"""

import json
import os
import platform
import subprocess
import sys
import re
import webbrowser
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List


# Version for linksaver
___version___: str = "3.0.0"


# ansi colors


# Python with ANSIColors
# by Shadowdara
#
# licensed under Appache 2.0
#


END = "\x1b[0m"
BOLD = "\x1b[1m"

ITALIC = "\x1b[3m"
UNDERLINED = "\x1b[4m"

REVERSE_TEXT = "\x1b[7m"

NOT_UNDERLINED = "\x1b[24m"

POSITIVE_TEXT = "\x1b[27m"

BLACK = "\x1b[30m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
PURPLE = "\x1b[35m"
CYAN = "\x1b[36m"
WHITE = "\x1b[37m"

BG_BLACK = "\x1b[40m"
BG_RED = "\x1b[41m"
BG_GREEN = "\x1b[42m"
BG_YELLOW = "\x1b[43m"
BG_BLUE = "\x1b[44m"
BG_PURPLE = "\x1b[45m"
BG_CYAN = "\x1b[46m"
BG_WHITE = "\x1b[47m"

BRIGHT_BLACK = "\x1b[90m"
BRIGHT_RED = "\x1b[91m"
BRIGHT_GREEM = "\x1b[92m"
BRIGHT_YELLOW = "\x1b[93m"
BRIGHT_BLUE = "\x1b[94m"
BRIGHT_PURLPE = "\x1b[95m"
BRIGHT_CYAN = "\x1b[96m"
BRIGHT_WHITE = "\x1b[97m"

BG_BRIGHT_BLACK = "\x1b[100m"
BG_BRIGHT_RED = "\x1b[101m"
BG_BRIGHT_GREEM = "\x1b[102m"
BG_BRIGHT_YELLOW = "\x1b[103m"
BG_BRIGHT_BLUE = "\x1b[104m"
BG_BRIGHT_PURLPE = "\x1b[105m"
BG_BRIGHT_CYAN = "\x1b[106m"
BG_BRIGHT_WHITE = "\x1b[107m"


# ---------- TYPES ----------

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
    name: str
    link: str
    version: str
    license: str | list[str] | None
    date: str


@dataclass
class Link4:
    link: str
    date: str


@dataclass
class AppConfig:
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

    note: Optional[str] = None


# ---------- CONSTANTS ----------

NOTE = (
    "This file was generated with linksaver from seg from the samengine project. "
    "https://samengine.js.org or https://github.com/shadowdara/seg"
)

SCHEMA_URL = (
    "https://raw.githubusercontent.com/ShadowDara/samengine/"
    "refs/heads/master/.samengine/shema.linksaver.json"
)


# ---------- PATH ----------

def configPath() -> Path:
    script_dir = Path(__file__).resolve().parent
    
    return script_dir / "linksaver.json"
    # return Path.cwd() / ".samengine" / "linksaver.json"

# ---------- PROMPT ----------

def prompt(message: str) -> str:
    """
    Wrapper function for an Input Prompt

    Args:
        message (str): String which gets printed to the command line

    Returns:
        str: input which the user types in
    """

    return input(message).strip()


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


def load() -> AppConfig:
    """
    function which loads the linksaver config

    Raises:
        Exception: _description_
        Exception: _description_

    Returns:
        AppConfig: The config data for the programm
    """
    
    file = configPath()

    if not file.exists():
        raise Exception("config not found")

    data = json.loads(file.read_text(encoding="utf8"))

    if not data.get("projectname"):
        raise Exception("projectname must be set")

    if "$schema" not in data:
        data["$schema"] = SCHEMA_URL
    
    if "settings" not in data:
        data["settings"] = newSettings()

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

    return config


# ---------- INIT ----------

def init():
    print("Init Linksaver")

    directory = Path.cwd() / ".samengine"
    directory.mkdir(parents=True, exist_ok=True)

    file = configPath()

    if file.exists():
        print(f"Config already exists: {file}")
        return

    (directory / "links.info.md").write_text("", encoding="utf8")
    (directory / "links.info.txt").write_text("", encoding="utf8")

    name = prompt("Projectname: ")

    config = newConfig(name)
    save(config)

    print(f"Created config at {file}")


# ---------- ADD ----------

def add(config: AppConfig):
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
    

# add4
# ersetzt Rust add2

def add4(config: AppConfig):
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


# add5
# ersetzt Rust add3

def add5(config: AppConfig):
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

def openLink(url: str):
    try:
        if platform.system() == "Windows":
            os.startfile(url)
        elif platform.system() == "Darwin":
            subprocess.run(["open", url], check=False)
        else:
            subprocess.run(["xdg-open", url], check=False)
    except Exception as e:
        print("Error opening link:", e)


def openAll(config: AppConfig):
    print("Opening links...")
    for link in config.links:
        openLink(link.link)



# ---------- MARKDOWN FORMAT ----------

def view(config: AppConfig):
    file = Path(".samengine/links.md")

    output = ""

    output += f"# Links for {config.projectname}\n\n"

    infoFile = Path(".samengine/links.info.md")

    if infoFile.exists():
        output += infoFile.read_text(encoding="utf8") + "\n\n"
    else:
        print("Info file doesnt exist!")

    output += f"Used for {config.projectname}:\n\n"

    # links
    for l in config.links:
        output += "- "

        if l.name:
            output += f"**{l.name}** "

        output += f"([{l.link}]({l.link})) "

        output += f"- {l.description} - "

        if l.author:
            output += f"by **{l.author}** "

        if l.license:
            output += f"licensed unter *{l.license}* "

        if l.licenselink:
            output += f"([{l.licenselink}]({l.licenselink})) "

        if l.changenotice:
            output += "- *(changes were made)*"

        if l.date:
            output += f" - *(saved at date: {l.date})*"

        output += "\n"

    # links2
    for l in config.links2:
        output += f"- {l}\n"

    # links4
    if config.links4 is not None:
        for l in config.links4:
            output += f"- {l.link} saved at date: **{l.date}**\n"

    # package lock
    if config.linkspkglock is not None:
        for item in config.linkspkglock:
            output += (
                f"- used **{item.name}** version {item.version} "
                f"licensed under **{item.license}** "
                f"- *[Link]({item.link})*\n"
            )

    # cargo lock
    if config.linkscargolock is not None:
        for item in config.linkscargolock:
            output += (
                f"- used **{item.name}** version {item.version} "
                f"licensed under **{item.license}** "
                f"- *[Link]({item.link})*\n"
            )

    # links3
    for licenseFile in config.links3:
        path = Path(licenseFile)

        if path.exists():
            content = path.read_text(encoding="utf8")

            output += f"""
---

**license content from file: {licenseFile}**

{content}

"""
        else:
            print(f"Warning: License file '{licenseFile}' does not exist.")

    # links5
    if config.links5 is not None:
        for item in config.links5:
            path = Path(item.link)

            if path.exists():
                content = path.read_text(encoding="utf8")

                output += f"""
---

**license content from file: {item.link}** at date: *{item.date}*

{content}

"""
            else:
                print(f"Warning: License file '{item.link}' does not exist.")

    output += """
---

*File generated by linksaver from s2* - [More Infos](https://shadowdara.wordpress.com/2026/06/30/minisite-a-site-in-only-one-html-file/)
"""

    file.write_text(output, encoding="utf8")

    print(
        """
Created File - Use parseMarkdown from samengine to make it into a nice html file.

npm i samengine
npx samengine markdown .samengine/links.md
"""
    )


# ---------- TXT FORMAT ----------

def viewx(config: AppConfig) -> None:
    """
    Function to convert the licenses in the JSON file into a TXT File
    """

    file = Path(".samengine/links.txt")

    output = ""

    output += f"Links for {config.projectname}\n\n"

    infoFile = Path(".samengine/links.info.txt")

    if infoFile.exists():
        output += infoFile.read_text(encoding="utf8") + "\n\n"
    else:
        print("Info file doesnt exist!")

    output += f"Used for {config.projectname}:\n\n"

    # links
    for l in config.links:
        output += "- "

        if l.name:
            output += l.name

        output += f" ({l.link}) "

        output += f"- {l.description} - "

        if l.author:
            output += f"by {l.author} "

        if l.license:
            output += f"licensed unter {l.license} "

        if l.licenselink:
            output += f"({l.licenselink}) "

        if l.changenotice:
            output += "- (changes were made)"

        if l.date:
            output += f" - (saved at date: {l.date})"

        output += "\n"

    # links2
    for l in config.links2:
        output += f"- {l}\n"

    # links4
    if config.links4 is not None:
        for l in config.links4:
            output += f"- {l.link} saved at date: {l.date}\n"

    # links3
    for licenseFile in config.links3:
        path = Path(licenseFile)

        if path.exists():
            content = path.read_text(encoding="utf8")

            output += f"""
license content from file: {licenseFile}

{content}

"""
        else:
            print(f"Warning: License file '{licenseFile}' does not exist.")

    # links5
    if config.links5 is not None:
        for item in config.links5:
            path = Path(item.link)

            if path.exists():
                content = path.read_text(encoding="utf8")

                output += f"""
license content from file: {item.link} at date: {item.date}

{content}

"""
            else:
                print(f"Warning: License file '{item.link}' does not exist.")

    output += """
---

File generated by linksaver from s2 - https://shadowdara.wordpress.com/2026/06/30/minisite-a-site-in-only-one-html-file/
"""

    file.write_text(output, encoding="utf8")


# ---------- LIST ----------

def list_links(config: AppConfig):
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

# ---------- ADD PACKAGE LOCK LICENSES ----------

def addPkgLock(config: AppConfig):
    lockFile = Path.cwd() / "package-lock.json"

    if not lockFile.exists():
        print("package-lock.json not found")
        return

    nodeModules = Path.cwd() / "node_modules"

    if not nodeModules.exists():
        print("node_modules not found. Run npm install first.")
        return

    with open(lockFile, "r", encoding="utf8") as f:
        lock = json.load(f)

    packages: list[PackageInfo] = []

    def readLicense(pkgPath: Path) -> str:
        try:
            with open(pkgPath / "package.json", "r", encoding="utf8") as f:
                pkgJson = json.load(f)

            if isinstance(pkgJson.get("license"), str):
                return pkgJson["license"]

            if isinstance(pkgJson.get("license"), dict):
                if isinstance(pkgJson["license"].get("type"), str):
                    return pkgJson["license"]["type"]

            if isinstance(pkgJson.get("licenses"), list):
                return ", ".join(
                    x if isinstance(x, str) else x.get("type", "")
                    for x in pkgJson["licenses"]
                )

            return "UNKNOWN"

        except Exception:
            return "UNKNOWN"

    # package-lock v2 / v3
    if "packages" in lock:
        for key, value in lock["packages"].items():

            if key == "":
                continue

            packagePath = Path.cwd() / key

            name = value.get("name") or re.sub(r"^node_modules/", "", key)

            packages.append(
                PackageInfo(
                    name=name,
                    version=value.get("version", ""),
                    license=readLicense(packagePath),
                    link=f"https://www.npmjs.com/package/{name}",
                    date=datetime.now().isoformat(),
                )
            )

    config.linkspkglock = packages

    save(config)

    print(f"Added {len(packages)} packages from package-lock.json")


# ---------- ADD CARGO LOCK LICENSES ----------

def addCargoLock(config: AppConfig):
    """
    Function to add all the licenses from Cargo packages

    Args:
        config (AppConfig): _description_

    Returns:
        _type_: _description_
    """
    
    lockFile = Path.cwd() / "Cargo.lock"

    if not lockFile.exists():
        print("Cargo.lock not found")
        return

    home = os.environ.get("HOME") or os.environ.get("USERPROFILE")

    if not home:
        print("Home directory not found")
        return

    cargoHome = Path(home) / ".cargo" / "registry" / "src"

    if not cargoHome.exists():
        print("Cargo registry not found.")
        print("Run: cargo fetch")
        return

    lock = lockFile.read_text(encoding="utf8")

    packages: list[PackageInfo] = []

    def findCargoToml(name: str, version: str) -> Path | None:
        """
        Function which searches for the cargo toml of a crate

        Args:
            name (str): Name of the crate
            version (str): Version of the crate

        Returns:
            Path | None: the path to the crate
        """
        for registry in cargoHome.iterdir():
            cargoToml = registry / f"{name}-{version}" / "Cargo.toml"

            if cargoToml.exists():
                return cargoToml

        return None

    def readLicense(cargoToml: Path) -> str:
        content = cargoToml.read_text(encoding="utf8")

        licenseMatch = re.search(
            r'^\s*license\s*=\s*"([^"]+)"',
            content,
            re.MULTILINE,
        )

        if licenseMatch:
            return licenseMatch.group(1)

        licenseFile = re.search(
            r'^\s*license-file\s*=\s*"([^"]+)"',
            content,
            re.MULTILINE,
        )

        if licenseFile:
            return "SEE LICENSE FILE"

        return "UNKNOWN"

    blocks = re.split(r"\[\[package\]\]", lock)

    seen: set[str] = set()

    for block in blocks:

        nameMatch = re.search(
            r'^\s*name\s*=\s*"([^"]+)"',
            block,
            re.MULTILINE,
        )

        versionMatch = re.search(
            r'^\s*version\s*=\s*"([^"]+)"',
            block,
            re.MULTILINE,
        )

        if not nameMatch or not versionMatch:
            continue

        name = nameMatch.group(1)
        version = versionMatch.group(1)

        identifier = f"{name}@{version}"

        if identifier in seen:
            continue

        seen.add(identifier)

        cargoToml = findCargoToml(name, version)

        packages.append(
            PackageInfo(
                name=name,
                version=version,
                license=readLicense(cargoToml) if cargoToml else "UNKNOWN",
                link=f"https://crates.io/crates/{name}",
                date=datetime.now().isoformat(),
            )
        )

    config.linkscargolock = packages

    save(config)

    print(f"Added {len(packages)} crates from Cargo.lock")


# ---------- HELP ----------

def help():
    print("""

██╗     ██╗███╗   ██╗██╗  ██╗███████╗ █████╗ ██╗   ██╗███████╗██████╗
██║     ██║████╗  ██║██║ ██╔╝██╔════╝██╔══██╗██║   ██║██╔════╝██╔══██╗
██║     ██║██╔██╗ ██║█████╔╝ ███████╗███████║██║   ██║█████╗  ██████╔╝
██║     ██║██║╚██╗██║██╔═██╗ ╚════██║██╔══██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
███████╗██║██║ ╚████║██║  ██╗███████║██║  ██║ ╚████╔╝ ███████╗██║  ██║
╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝

by shadowdara

=== Commands ===

help      show this message
init      create config
add       add link
add2      add entry (text only)
add3      add license file
view      formats links into Markdown
viewx     formats links into TXT
list      list links
addpkg    add links from a package lock file
addcargo  add links from a cargo lock file
open      open all links
info      get more infos about the programm

""")


def info() -> None:
    """
    Function which generated an Info on how to use the Programm (TODO)
    """


# Menu
def menu() -> str:
    """
    Selection Menu in Command line so User down have to select the options
    via CLI Args
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


# ---------- EXECUTE ----------

def execute(arg: str, config: AppConfig) -> None:
    if arg in ("help", "-h", "--help"):
        help()
        return

    if arg == "info":
        info()
        return

    if arg == "init":
        init()
        return

    if arg == "add":
        add(config)

    elif arg == "add2":
        add4(config)

    elif arg == "add3":
        add5(config)

    elif arg == "view":
        view(config)

    elif arg == "viewx":
        viewx(config)

    elif arg == "list":
        list_links(config)

    elif arg == "addpkg":
        addPkgLock(config)

    elif arg == "addcargo":
        addCargoLock(config)

    elif arg == "open":
        openAll(config)
    
    else:
        print("Linksaver: Argument not found!")


# Main
def main() -> None:
    """
    Main function which executes the programm
    """

    # Try loading the Config
    try:
        # Load the Config
        config: AppConfig = load()

        if config.settings is not None:
            if config.settings.selectmenu is True:
                # Select via a cli selector
                arg = menu()

                # Execute the selection
                execute(arg, config)

                # finish
                return


        # More than one argument
        # then run linksaver in cli mode
        if len(sys.argv) > 1:
            # get first arg after the filename
            arg = sys.argv[1]

            execute(arg, config)
        else:
            print("Linksaver: run with one argument of help!")

    except Exception as e:
        # When a Config Error Appears
        print("Linksaver: Config Error:", e)
        print("Run 'init' first or run with help!")
        
        input()
        sys.exit(1)


# Main stuff where everthing gets executed
if __name__ == "__main__":
    main()
    sys.exit(0)
