"""
Commands that scan a dependency lockfile and turn every package into a
PackageInfo credit entry:

    add_package_lock() -> CLI `addpkg`     reads package-lock.json (npm)
    add_cargo_lock()   -> CLI `addcargo`   reads Cargo.lock (Rust/cargo)
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ..config import AppConfig, save
from ..models import PackageInfo


# ---------- NPM: package-lock.json ----------

def add_package_lock(config: AppConfig) -> None:
    """
    CLI `addpkg`: read package-lock.json + node_modules/*/package.json to
    collect the name/version/license of every installed npm package.
    """

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

    packages: List[PackageInfo] = []

    def readLicense(pkgPath: Path) -> str:
        """Best-effort extraction of the `license` field from package.json."""

        try:
            with open(pkgPath / "package.json", "r", encoding="utf8") as f:
                pkgJson = json.load(f)

            # Modern format: "license": "MIT"
            if isinstance(pkgJson.get("license"), str):
                return pkgJson["license"]

            # Older format: "license": { "type": "MIT" }
            if isinstance(pkgJson.get("license"), dict):
                if isinstance(pkgJson["license"].get("type"), str):
                    return pkgJson["license"]["type"]

            # Even older format: "licenses": [{ "type": "MIT" }, ...]
            if isinstance(pkgJson.get("licenses"), list):
                return ", ".join(
                    x if isinstance(x, str) else x.get("type", "")
                    for x in pkgJson["licenses"]
                )

            return "UNKNOWN"

        except Exception:
            return "UNKNOWN"

    # package-lock.json v2/v3 store every dependency under "packages",
    # keyed by its path inside node_modules (e.g. "node_modules/react").
    if "packages" in lock:
        for key, value in lock["packages"].items():

            if key == "":
                # The "" key describes the root project itself - skip it.
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


# ---------- CARGO: Cargo.lock ----------

def add_cargo_lock(config: AppConfig) -> None:
    """
    CLI `addcargo`: read Cargo.lock and, for every crate, look up its
    license from the locally cached Cargo.toml in ~/.cargo/registry.

    Requires `cargo fetch` to have been run at least once so the crate
    sources are present in the local registry cache.
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

    packages: List[PackageInfo] = []

    def findCargoToml(name: str, version: str) -> Optional[Path]:
        """
        Search every registry mirror folder under ~/.cargo/registry/src
        for this crate@version's Cargo.toml.
        """

        for registry in cargoHome.iterdir():
            cargoToml = registry / f"{name}-{version}" / "Cargo.toml"

            if cargoToml.exists():
                return cargoToml

        return None

    def readLicense(cargoToml: Path) -> str:
        """Extract the `license` (or `license-file`) field from Cargo.toml."""

        content = cargoToml.read_text(encoding="utf8")

        licenseMatch = re.search(
            r'^\s*license\s*=\s*"([^"]+)"', content, re.MULTILINE,
        )

        if licenseMatch:
            return licenseMatch.group(1)

        licenseFile = re.search(
            r'^\s*license-file\s*=\s*"([^"]+)"', content, re.MULTILINE,
        )

        if licenseFile:
            return "SEE LICENSE FILE"

        return "UNKNOWN"

    # Cargo.lock is a TOML file; rather than pulling in a TOML parser we
    # split on the "[[package]]" table headers and regex out the two
    # fields we care about from each block. Good enough for this format,
    # since Cargo.lock is machine-generated and very regular.
    blocks = re.split(r"\[\[package\]\]", lock)

    seen: set[str] = set()

    for block in blocks:
        nameMatch = re.search(r'^\s*name\s*=\s*"([^"]+)"', block, re.MULTILINE)
        versionMatch = re.search(r'^\s*version\s*=\s*"([^"]+)"', block, re.MULTILINE)

        if not nameMatch or not versionMatch:
            continue

        name = nameMatch.group(1)
        version = versionMatch.group(1)

        # Cargo.lock can list the same crate more than once in edge
        # cases; de-duplicate by "name@version".
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
