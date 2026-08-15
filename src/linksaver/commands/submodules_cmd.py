"""
Commands that manage the list of "git submodules" recorded in the config
(config.git.submodules), which is Linksaver's own lightweight alternative
to real `.gitmodules` submodules:

    add_git_submodule()   -> CLI `addsubmodule`  register a repo to clone later
    clone_git_submodules() -> CLI `clonesubm`/`c` actually clone every one of them
"""

import os
import subprocess

from ..config import AppConfig, save
from ..models import GitData, Submodules
from .prompts import prompt


def add_git_submodule(config: AppConfig) -> None:
    """
    CLI `addsubmodule`: interactively record the info needed to clone a
    dependency repository later (see clone_git_submodules()).

    Args:
        config: the config of the program
    """

    desc = prompt("Description: ")
    dirrr = prompt("Dir (where git clone is executed): ")
    clonedir = prompt("The name for the repo dir: ")
    repolink = prompt("repo link: ")
    repocommit = prompt("repo commit: ")
    branch = prompt("Repo Branch (empty for the main branch): ")

    if branch == "":
        branch = None

    module = Submodules(
        dir=dirrr,
        repolink=repolink,
        repocommit=repocommit,
        clonedir=clonedir,
        desc=desc,
        branch=branch,
    )

    if config.git is None:
        config.git = GitData()

    config.git.submodules.append(module)

    # DONT FORGET SAVING!
    save(config)

    print("Added new submodule")


def clone_git_submodules(config: AppConfig) -> None:
    """
    CLI `clonesubm` / `c`: clone every submodule registered via
    add_git_submodule(), check out its pinned commit, initialize its own
    (real) git submodules recursively, and then recurse into l2's own
    dependency chain by calling `l2 clonesubm` inside the freshly cloned
    repo.
    """

    print("Cloning depencies")

    old_path = os.getcwd()

    if config.git is None:
        print("git option is None!")
        return

    for e in config.git.submodules:
        # Always start from the original working directory for each entry.
        os.chdir(old_path)

        print(e.desc)

        # Make sure the target directory exists before cloning into it.
        os.makedirs(os.getcwd() + "/" + e.dir, exist_ok=True)
        os.chdir(os.getcwd() + "/" + e.dir)

        # Build the clone command, using the pinned branch if one was set.
        if e.branch:
            clone_command = (
                f'git clone --recursive --branch "{e.branch}" '
                f'"{e.repolink}" "{e.clonedir}"'
            )
        else:
            clone_command = (
                f'git clone --recursive '
                f'"{e.repolink}" "{e.clonedir}"'
            )

        subprocess.run(clone_command, shell=True)

        # Move into the freshly cloned repo to pin it to the exact commit.
        os.chdir(os.getcwd() + "/" + e.clonedir)

        checkout_command = "git checkout " + e.repocommit
        subprocess.run(checkout_command, shell=True)

        subprocess.run("git submodule update --init --recursive", shell=True)

        # Recurse: let l2 clone *this* repo's own submodules too.
        subprocess.run("l2 clonesubm", shell=True)

        print(f"Cloned {e.clonedir} successfuly!")

    print("Finished cloning every submodule!")
