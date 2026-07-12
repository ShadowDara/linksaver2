# Git Splitter

import os
from pathlib import Path
from dataclasses import dataclass
from .config import AppConfig, GitData, save
from typing import Optional, List, Union
import json
import shutil


@dataclass
class gitsplitterdata:
    """
    Settings for the git splitter
    the maxfilesize is in Megabytes
    """

    maxfilesize: int
    ignorepath: List[str]


def get_splitter_folder(repo: Path) -> Path:
    return repo / ".samengine" / "git-splitter"


def find_large_files_in_git_repo(repo_path: str, config: AppConfig) -> List[Path]:
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

        if any(
            relative == ignore or relative.startswith(ignore + "/")
            for ignore in ignore_paths
        ):
            continue

        if file.stat().st_size >= max_size:
            files.append(file)

    return files


# Beispiel:
#files = find_large_files_in_git_repo(".", min_size_mb=50)

#for filename, size in files:
#    print(f"{size:.2f} MB  {filename}")


def check_git(config: AppConfig) -> None:
    # Check if executed in the git root
    gitfolder = Path('.git')

    if not gitfolder.exists():
        print('git folder not found')
        print('Please run in the git root folder')
        return


def check_settings(config: AppConfig) -> AppConfig:
    changed = False

    if config.git is None:
        config.git = GitData()
        changed = True

    if config.git.splitter is None:
        config.git.splitter = gitsplitterdata(
            maxfilesize=99,
            ignorepath=[]
        )
        changed = True


    save(config)

    return config


def view(config: AppConfig) -> None:
    repo = Path.cwd()
    
    print(f"Max file size: {config.git.splitter.maxfilesize} MB")
    
    files = find_large_files_in_git_repo(
        os.getcwd(),
        config
    )

    if not files:
        print("No files over maxsize found!.")
        return

    for file in files:
        size = file.stat().st_size / 1024 / 1024
        print(f"{size:.2f} MB  {file.relative_to(repo).as_posix()}")


def restore(config: AppConfig) -> None:
    repo = Path.cwd()

    split_folder = get_splitter_folder(repo)

    manifest_file = split_folder / "manifest.json"

    if not manifest_file.exists():
        print("No split manifest found.")
        return


    with open(
        manifest_file,
        encoding="utf-8"
    ) as f:
        manifest = json.load(f)


    for entry in manifest:

        original = repo / entry["file"]

        original.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(original, "wb") as output:

            for part in entry["parts"]:

                part_file = repo / part

                with open(part_file, "rb") as src:
                    shutil.copyfileobj(
                        src,
                        output
                    )


        print(
            f"restored: {original}"
        )


    # Cleanup
    shutil.rmtree(split_folder)


def split(config: AppConfig) -> None:
    repo = Path.cwd()

    files = find_large_files_in_git_repo(
        str(repo),
        config
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

        # Original entfernen
        #file.unlink()

        manifest.append({
            "file": str(relative).replace("\\", "/"),
            "parts": parts
        })

        print(
            f"splitted: {file.relative_to(repo).as_posix()}"
        )


    with open(
        split_folder / "manifest.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            manifest,
            f,
            indent=4
        )


###############
# CLI STRUCTURE

def index(config: AppConfig):
    check_git(config)
    config = check_settings(config)

    view(config)


def splitter(config: AppConfig):
    check_git(config)
    config = check_settings(config)

    split(config)


def restore_splitter(config: AppConfig):
    check_git(config)
    config = check_settings(config)

    restore(config)
