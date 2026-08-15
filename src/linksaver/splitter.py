"""
Git splitter
============

Some git hosting providers (and git itself) struggle with very large
files. This module implements a small "splitter" feature:

1. ``view``    - scan the repo and list every file at/above the configured
                 size limit.
2. ``split``   - cut each such file into fixed-size chunks stored under
                 ``.samengine/git-splitter/`` (safe to commit) and write a
                 manifest describing how to put them back together.
3. ``restore`` - use the manifest to reassemble the original files.

The size limit and list of ignored paths are configured per-project via
``config.git.splitter`` (see models.GitSplitterData).
"""

import json
import os
import shutil
from pathlib import Path
from typing import List

from .config import AppConfig, save
from .models import GitData, GitSplitterData

# Backwards-compatible alias: this dataclass used to be defined directly
# in this module under a lowercase name. Some external code may still
# import `splitter.gitsplitterdata`, so we keep the name available here.
gitsplitterdata = GitSplitterData


# ---------- PATHS ----------

def get_splitter_folder(repo: Path) -> Path:
    """Folder where split file-chunks and the manifest are stored."""

    return repo / ".samengine" / "git-splitter"


# ---------- FINDING LARGE FILES ----------

def find_large_files_in_git_repo(repo_path: str, config: AppConfig) -> List[Path]:
    """
    Walk the whole repo and return every file at/above the configured
    size limit, skipping .git/, .samengine/ and any ignored paths.

    Args:
        repo_path: Root directory of the repository to scan.
        config: Project config (used for the size limit + ignore list).

    Returns:
        List of absolute Paths to oversized files.
    """

    repo = Path(repo_path).resolve()

    ignore_paths = []

    if config.git and config.git.splitter:
        ignore_paths = [
            Path(p).as_posix()
            for p in config.git.splitter.ignorepath
        ]

    max_size = config.git.splitter.maxfilesize * 1024 * 1024

    files = []

    for file in repo.rglob("*"):
        if not file.is_file():
            continue

        if ".git" in file.parts:
            continue

        if ".samengine" in file.parts:
            continue

        relative = file.relative_to(repo).as_posix()

        # Skip anything under an ignored path (exact match or prefix).
        if any(
            relative == ignore or relative.startswith(ignore + "/")
            for ignore in ignore_paths
        ):
            continue

        if file.stat().st_size >= max_size:
            files.append(file)

    return files


# ---------- SETUP / SANITY CHECKS ----------

def check_git(config: AppConfig) -> None:
    """Warn (and stop) if the command isn't run from a git repo root."""

    gitfolder = Path(".git")

    if not gitfolder.exists():
        print("git folder not found")
        print("Please run in the git root folder")
        return


def check_settings(config: AppConfig) -> AppConfig:
    """
    Make sure `config.git` / `config.git.splitter` exist, creating them
    with sane defaults (and persisting the change) if they don't.
    """

    changed = False

    if config.git is None:
        config.git = GitData()
        changed = True

    if config.git.splitter is None:
        config.git.splitter = GitSplitterData(
            maxfilesize=99,
            ignorepath=[],
        )
        changed = True

    if changed:
        save(config)

    return config


# ---------- VIEW ----------

def view(config: AppConfig) -> None:
    """Print every oversized file currently tracked in the repo."""

    repo = Path.cwd()

    print(f"Max file size: {config.git.splitter.maxfilesize} MB")

    files = find_large_files_in_git_repo(
        os.getcwd(),
        config,
    )

    if not files:
        print("No files over maxsize found!.")
        return

    for file in files:
        size = file.stat().st_size / 1024 / 1024
        print(f"{size:.2f} MB  {file.relative_to(repo).as_posix()}")


# ---------- RESTORE ----------

def restore(config: AppConfig) -> None:
    """
    Reassemble every file that was previously split, using the manifest
    written by split(), then remove the temporary split folder.
    """

    repo = Path.cwd()
    split_folder = get_splitter_folder(repo)
    manifest_file = split_folder / "manifest.json"

    if not manifest_file.exists():
        print("No split manifest found.")
        return

    with open(manifest_file, encoding="utf-8") as f:
        manifest = json.load(f)

    for entry in manifest:
        original = repo / entry["file"]
        original.parent.mkdir(parents=True, exist_ok=True)

        # Concatenate every chunk back into the original file, in order.
        with open(original, "wb") as output:
            for part in entry["parts"]:
                part_file = repo / part

                with open(part_file, "rb") as src:
                    shutil.copyfileobj(src, output)

        print(f"restored: {original}")

    # Clean up the chunk folder now that everything is restored.
    shutil.rmtree(split_folder)


# ---------- SPLIT ----------

def split(config: AppConfig) -> None:
    """
    Find every oversized file and cut it into fixed-size chunks stored
    under .samengine/git-splitter/, writing a manifest.json describing how
    to put everything back together with restore().
    """

    repo = Path.cwd()

    files = find_large_files_in_git_repo(
        str(repo),
        config,
    )

    if not files:
        print("No files to split found.")
        return

    split_folder = get_splitter_folder(repo)
    split_folder.mkdir(parents=True, exist_ok=True)

    manifest = []

    chunk_size = (
        config.git.splitter.maxfilesize
        * 1024
        * 1024
    )

    for file in files:
        relative = file.relative_to(repo)

        target = split_folder / relative
        target.mkdir(parents=True, exist_ok=True)

        parts = []

        with open(file, "rb") as src:
            index = 0

            while True:
                data = src.read(chunk_size)

                if not data:
                    break

                part = target / f"{file.name}.part{index:04d}"

                with open(part, "wb") as dst:
                    dst.write(data)

                parts.append(
                    str(part.relative_to(repo)).replace("\\", "/")
                )

                index += 1

        # NOTE: the original large file is intentionally left in place -
        # deleting it here would be destructive. Uncomment if you want
        # split() to remove the source file once it has been chunked:
        # file.unlink()

        manifest.append({
            "file": str(relative).replace("\\", "/"),
            "parts": parts,
        })

        print(f"splitted: {file.relative_to(repo).as_posix()}")

    with open(split_folder / "manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)


# ---------------------------------------------------------------------------
# CLI-facing wrappers
#
# These three functions are what cli.py actually calls. Each one does the
# same "make sure we're in a git repo + settings exist" dance before
# calling the real implementation above - keeping that boilerplate here
# instead of repeating it in cli.py.
# ---------------------------------------------------------------------------

def index(config: AppConfig) -> None:
    """CLI command: `gitview` - list oversized files."""

    check_git(config)
    config = check_settings(config)
    view(config)


def splitter(config: AppConfig) -> None:
    """CLI command: `gitsplit` - split oversized files into chunks."""

    check_git(config)
    config = check_settings(config)
    split(config)


def restore_splitter(config: AppConfig) -> None:
    """CLI command: `gitrestore` - reassemble previously split files."""

    check_git(config)
    config = check_settings(config)
    restore(config)
