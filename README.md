# Linksaver (`l2`)

<p align="center">
  <b>Save, organize and document your project links, licenses and dependencies.</b>
</p>

Linksaver is a command-line tool for developers who want to keep track of external resources used in their projects.

The CLI command is:

```bash
l2
```

Linksaver stores all information in a structured `linksaver.json` file and can generate Markdown and TXT documentation containing:

* Project links
* Credits
* Licenses
* License files
* Package dependencies
* Cargo dependencies
* Git submodules

---

# Features

✅ Save project links
✅ Store author and license information
✅ Generate Markdown documentation
✅ Generate TXT license reports
✅ Import npm dependencies from `package-lock.json`
✅ Import Rust dependencies from `Cargo.lock`
✅ Manage Git submodules
✅ Open saved links in your browser
✅ JSON based configuration
✅ Cross-platform support

Supported platforms:

* Windows
* Linux
* macOS

---

# Installation

Install from PyPI:

```bash
pip install linksaver
```

After installation:

```bash
l2 help
```

should work.

---

# Quick Start

Initialize Linksaver in your project:

```bash
l2 init
```

Example:

```text
Init Linksaver

Projectname: MyProject

Created config at linksaver.json
```

Your project now contains:

```text
MyProject/
│
├── linksaver.json
└── .samengine/
    ├── links.info.md
    └── links.info.txt
```

---

# Basic Usage

## Add a link

```bash
l2 add
```

Example:

```text
Name:
SDL2

Author:
SDL Team

License:
zlib

New Link:
https://github.com/libsdl-org/SDL

Description:
Cross platform multimedia library
```

---

## List saved links

```bash
l2 list
```

Example:

```text
"SDL2"
https://github.com/libsdl-org/SDL

by SDL Team

licensed under zlib
```

---

## Generate documentation

Generate Markdown:

```bash
l2 view
```

Creates:

```text
.samengine/links.md
```

Generate TXT:

```bash
l2 viewx
```

Creates:

```text
.samengine/links.txt
```

---

# Dependency Tracking

## npm / Node.js

Import dependencies from:

```text
package-lock.json
```

Run:

```bash
l2 addpkg
```

Linksaver collects:

* Package name
* Version
* License
* npm URL
* Date

Example:

```json
{
    "name": "typescript",
    "version": "5.x",
    "license": "Apache-2.0"
}
```

---

## Rust / Cargo

Import dependencies from:

```text
Cargo.lock
```

Run:

```bash
l2 addcargo
```

Requires:

```bash
cargo fetch
```

Linksaver collects:

* Crate name
* Version
* License
* crates.io URL

---

# Git Submodules

Linksaver can store and clone external repositories.

Add a submodule:

```bash
l2 addsubmodule
```

Clone all saved repositories:

```bash
l2 clonesubm
```

Example:

```text
Cloning dependencies

wxWidgets source

Cloned wxWidgets successfully!

Finished cloning every submodule!
```

---

# Configuration

The main configuration file:

```text
linksaver.json
```

Example:

```json
{
    "projectname": "Example",

    "pretty": true,

    "links": [],

    "linkspkglock": [],

    "linkscargolock": [],

    "settings": {
        "selectmenu": false
    },

    "git": {
        "submodules": []
    }
}
```

---

# Interactive Menu

Enable the menu system:

```json
{
    "settings": {
        "selectmenu": true
    }
}
```

Now running:

```bash
l2
```

opens an interactive menu.

---

# Commands

| Command        | Description               |
| -------------- | ------------------------- |
| `help`         | Show help                 |
| `init`         | Create configuration      |
| `add`          | Add link                  |
| `add2`         | Add text entry            |
| `add3`         | Add license file          |
| `view`         | Generate Markdown         |
| `viewx`        | Generate TXT              |
| `list`         | Show credits              |
| `addpkg`       | Import npm dependencies   |
| `addcargo`     | Import Cargo dependencies |
| `open`         | Open all links            |
| `addsubmodule` | Add Git submodule         |
| `clonesubm`    | Clone Git submodules      |

---

# Why Linksaver?

Many projects use external libraries, assets and tools but often forget to document them.

Linksaver helps with:

* Open source compliance
* Creating credits pages
* License documentation
* Dependency tracking
* Project maintenance

---

# Development

Linksaver is written in:

```text
Python
```

Main technologies:

* Python Dataclasses
* JSON
* pathlib
* subprocess
* Git integration

---

# License

Linksaver is licensed under:

```
Apache License 2.0
```

Copyright:

```
ShadowDara 2026
```

---

# Links

Documentation:

```
https://shadowdara.github.io/docs/#/linksaver
```

---

# Version

Current version:

```
3.0.0
```

---

Made with ❤️ by **ShadowDara**
