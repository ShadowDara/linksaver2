
#!/usr/bin/env python3

import argparse
import base64
import getpass
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


VERSION = 1


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def find_main_git_repo(path: Path) -> Path:
    """Find the git repository containing path."""
    path = path.resolve()

    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"{path} ist kein Git-Repository.")

    return Path(result.stdout.strip()).resolve()


def is_git_repository(path: Path) -> bool:
    """Check whether path is a Git repository."""
    git_path = path / ".git"

    if git_path.is_dir():
        return True

    if git_path.is_file():
        # Worktrees/submodules can have a .git file.
        try:
            content = git_path.read_text(errors="ignore")
            return content.startswith("gitdir:")
        except OSError:
            return False

    return False


def find_nested_repositories(main_repo: Path, output_dir: Path | None):
    """
    Find all Git repositories below main_repo.

    The main repository itself is excluded.
    """
    repositories = []

    output_dir = output_dir.resolve() if output_dir else None

    for root, dirs, files in os.walk(main_repo):
        root_path = Path(root).resolve()

        # Never descend into the main .git.
        if root_path == main_repo / ".git":
            dirs[:] = []
            continue

        # Ignore output directory.
        if output_dir and (
            root_path == output_dir
            or output_dir in root_path.parents
        ):
            dirs[:] = []
            continue

        # Check for .git directory.
        if ".git" in dirs:
            repo = root_path

            if repo != main_repo:
                repositories.append(repo)

            # Do not search inside nested repository's .git directory.
            dirs.remove(".git")

        # Check for .git file.
        if ".git" in files:
            repo = root_path

            if repo != main_repo:
                repositories.append(repo)

    return sorted(set(repositories))


# ---------------------------------------------------------------------------
# ZIP creation
# ---------------------------------------------------------------------------

def zip_git_directory(repo: Path, archive: Path):
    """
    Create a ZIP containing only the repository's .git entry.
    """
    git_path = repo / ".git"

    if not git_path.exists():
        raise RuntimeError(f"Kein .git gefunden: {repo}")

    archive.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(
        archive,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as zf:

        metadata = {
            "format_version": VERSION,
            "repository": repo.name,
            "original_path": str(repo),
            "git_type": "directory" if git_path.is_dir() else "file",
        }

        zf.writestr(
            "gitpack.json",
            json.dumps(metadata, indent=2, ensure_ascii=False),
        )

        if git_path.is_file():
            zf.write(
                git_path,
                ".git",
            )
            return

        for root, dirs, files in os.walk(git_path):
            root_path = Path(root)

            # Stable output.
            dirs.sort()
            files.sort()

            for filename in files:
                file_path = root_path / filename
                relative = file_path.relative_to(repo)

                zf.write(
                    file_path,
                    relative.as_posix(),
                )


# ---------------------------------------------------------------------------
# Encryption
# ---------------------------------------------------------------------------

def openssl_available() -> bool:
    return shutil.which("openssl") is not None


def encrypt_file(source: Path, destination: Path, password: str):
    """
    Encrypt using OpenSSL AES-256-CBC.

    The password is passed through stdin instead of appearing in the
    process command line.
    """
    if not openssl_available():
        raise RuntimeError(
            "openssl wurde nicht gefunden. "
            "Installiere OpenSSL oder verwende --no-encrypt."
        )

    command = [
        "openssl",
        "enc",
        "-aes-256-cbc",
        "-pbkdf2",
        "-iter",
        "200000",
        "-salt",
        "-in",
        str(source),
        "-out",
        str(destination),
    ]

    result = subprocess.run(
        command,
        input=password + "\n",
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Verschlüsselung fehlgeschlagen:\n"
            + result.stderr.strip()
        )


def decrypt_file(source: Path, destination: Path, password: str):
    """Decrypt an OpenSSL AES-256-CBC archive."""
    if not openssl_available():
        raise RuntimeError("openssl wurde nicht gefunden.")

    command = [
        "openssl",
        "enc",
        "-d",
        "-aes-256-cbc",
        "-pbkdf2",
        "-iter",
        "200000",
        "-in",
        str(source),
        "-out",
        str(destination),
    ]

    result = subprocess.run(
        command,
        input=password + "\n",
        text=True,
        capture_output=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Entschlüsselung fehlgeschlagen. "
            "Passwort korrekt?\n"
            + result.stderr.strip()
        )


# ---------------------------------------------------------------------------
# Base64
# ---------------------------------------------------------------------------

def encode_base64(source: Path, destination: Path):
    with source.open("rb") as src, destination.open("wb") as dst:
        base64.encode(src, dst)


def decode_base64(source: Path, destination: Path):
    with source.open("rb") as src, destination.open("wb") as dst:
        base64.decode(src, dst)


# ---------------------------------------------------------------------------
# Pack
# ---------------------------------------------------------------------------

def pack(args):
    main_repo = find_main_git_repo(Path(args.root))
    output_dir = Path(args.output).resolve()

    print(f"Main-Repository: {main_repo}")
    print(f"Ausgabe:          {output_dir}")
    print()

    repositories = find_nested_repositories(
        main_repo,
        output_dir,
    )

    if not repositories:
        print("Keine verschachtelten Git-Repositories gefunden.")
        return

    print(f"{len(repositories)} Repository(s) gefunden:\n")

    password = None

    if args.encrypt:
        password = getpass.getpass("Passwort: ")
        password_confirm = getpass.getpass("Passwort wiederholen: ")

        if password != password_confirm:
            raise RuntimeError("Passwörter stimmen nicht überein.")

        if not password:
            raise RuntimeError("Leeres Passwort ist nicht erlaubt.")

    output_dir.mkdir(parents=True, exist_ok=True)

    for repo in repositories:
        relative_repo = repo.relative_to(main_repo)

        # Make the output name unique and filesystem-friendly.
        safe_name = "_".join(relative_repo.parts)

        zip_path = output_dir / f"{safe_name}.git.zip"

        print(f"Packe: {relative_repo}")

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)

            plain_zip = tmp / "archive.zip"
            zip_git_directory(repo, plain_zip)

            final_file = zip_path

            if args.encrypt:
                encrypted = tmp / "archive.zip.enc"
                encrypt_file(
                    plain_zip,
                    encrypted,
                    password,
                )

                if args.base64:
                    final_file = output_dir / f"{safe_name}.git.zip.enc.b64"
                    encode_base64(encrypted, final_file)
                else:
                    final_file = output_dir / f"{safe_name}.git.zip.enc"
                    shutil.copy2(encrypted, final_file)

            elif args.base64:
                final_file = output_dir / f"{safe_name}.git.zip.b64"
                encode_base64(plain_zip, final_file)

            else:
                shutil.copy2(plain_zip, final_file)

        size = final_file.stat().st_size

        print(f"  -> {final_file}")
        print(f"     {size:,} Bytes")
        print()

    print("Fertig.")


# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------

def restore(args):
    archive = Path(args.archive).resolve()
    destination = Path(args.destination).resolve()

    if not archive.exists():
        raise RuntimeError(f"Archiv nicht gefunden: {archive}")

    password = None

    # Determine format.
    is_base64 = archive.name.endswith(".b64")
    is_encrypted = (
        ".enc" in archive.name
        or args.decrypt
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        current = archive

        # Base64 decode first.
        if is_base64:
            decoded = tmp / "decoded"
            print("Base64 dekodieren...")
            decode_base64(current, decoded)
            current = decoded

        # Decrypt next.
        if is_encrypted:
            password = getpass.getpass("Passwort: ")

            decrypted = tmp / "archive.zip"

            print("Entschlüsseln...")
            decrypt_file(
                current,
                decrypted,
                password,
            )

            current = decrypted

        # Validate ZIP.
        if not zipfile.is_zipfile(current):
            raise RuntimeError(
                "Die Datei ist kein gültiges ZIP-Archiv."
            )

        with zipfile.ZipFile(current, "r") as zf:
            names = zf.namelist()

            if "gitpack.json" not in names:
                raise RuntimeError(
                    "Kein gültiges gitpack-Archiv "
                    "(gitpack.json fehlt)."
                )

            metadata = json.loads(
                zf.read("gitpack.json")
            )

            print()
            print("Archiv:")
            print(f"  Repository: {metadata.get('repository')}")
            print(f"  Original:   {metadata.get('original_path')}")
            print(f"  Git-Typ:    {metadata.get('git_type')}")
            print()

            destination.mkdir(
                parents=True,
                exist_ok=True,
            )

            # Security: prevent ZIP path traversal.
            for name in names:
                target = (destination / name).resolve()

                if target != destination and destination not in target.parents:
                    raise RuntimeError(
                        f"Unsicherer ZIP-Pfad erkannt: {name}"
                    )

            print(f"Stelle .git wieder her nach:")
            print(f"  {destination}")

            for name in names:
                if name == "gitpack.json":
                    continue

                target = destination / name

                if name == ".git":
                    target.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                else:
                    target.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                with zf.open(name) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)

    print()
    print("Restore abgeschlossen.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def create_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Packt .git-Verzeichnisse verschachtelter "
            "Git-Repositories."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    # pack
    pack_parser = subparsers.add_parser(
        "pack",
        help="Verschachtelte .git-Verzeichnisse archivieren.",
    )

    pack_parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Main-Git-Repository (Default: aktuelles Verzeichnis).",
    )

    pack_parser.add_argument(
        "-o",
        "--output",
        default="./git-archives",
        help="Ausgabe-Verzeichnis.",
    )

    pack_parser.add_argument(
        "--encrypt",
        action="store_true",
        help="Archiv mit AES-256 verschlüsseln.",
    )

    pack_parser.add_argument(
        "--base64",
        action="store_true",
        help="Archiv zusätzlich als Base64 speichern.",
    )

    pack_parser.set_defaults(func=pack)

    # restore
    restore_parser = subparsers.add_parser(
        "restore",
        help="Ein .git-Archiv wiederherstellen.",
    )

    restore_parser.add_argument(
        "archive",
        help="ZIP/ENC/B64-Archiv.",
    )

    restore_parser.add_argument(
        "destination",
        help="Ziel-Repository.",
    )

    restore_parser.add_argument(
        "--decrypt",
        action="store_true",
        help="Archiv entschlüsseln.",
    )

    restore_parser.set_defaults(func=restore)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        args.func(args)

    except KeyboardInterrupt:
        print("\nAbgebrochen.")
        sys.exit(130)

    except Exception as exc:
        print(f"\nFEHLER: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()