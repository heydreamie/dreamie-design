"""Validate the portable skill and optionally build its installable ZIP.

Uses only the Python standard library. This check complements source and
behavioral review; it is not a full secret scanner or a visual acceptance test.
"""

import argparse
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit


MODULES = ("layout", "color", "traditional-color", "pattern", "art-analysis", "ai-style")
PRIVATE_PATH = re.compile(r"(?i)(?:\b[A-Z]:[\\/]|file://|/Users/|/home/|\\\\[^\\/\s]+[\\/])")
EMAIL = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9._%+-]*@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
RAW_SOURCE_NAME = re.compile(r"(?i)(?:full[-_.]?ocr|raw[-_.]?(?:ocr|text)|full[-_.]?text|全量OCR|全书文本)")
SECRET = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,})")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
TEXT_EXTENSIONS = {
    ".md", ".yaml", ".yml", ".txt", ".svg", ".json", ".json5",
    ".toml", ".ini", ".cfg", ".xml", ".html", ".css", ".js", ".mjs",
    ".py", ".sh", ".ps1", ".csv", ".tsv",
}
FORBIDDEN_EXTENSIONS = {".pdf", ".jsonl", ".sqlite", ".db", ".pem", ".key"}


def package_files(root):
    files = [root / "SKILL.md"]
    for folder_name in ("references", "agents", "assets"):
        folder = root / folder_name
        if folder.exists():
            files.extend(path for path in folder.rglob("*") if path.is_file() or path.is_symlink())
    for filename in ("README.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE", "LICENSE.md"):
        path = root / filename
        if path.is_file():
            files.append(path)
    return sorted(set(files))


def validate(root):
    errors = []
    skill = root / "SKILL.md"
    if not skill.is_file():
        return ["missing SKILL.md"]
    content = skill.read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---(?:\n|$)", content, re.S)
    if not frontmatter:
        errors.append("invalid skill frontmatter")
    else:
        header = frontmatter.group(1)
        if not re.search(r"^name: dreamie-design$", header, re.M):
            errors.append("skill name must be dreamie-design")
        if not re.search(r"^description: Use when .+", header, re.M):
            errors.append("description must declare a Use when trigger")

    for module in MODULES:
        for filename in ("guide.md", "methods.md", "sources.md"):
            path = root / "references" / module / filename
            if not path.is_file():
                errors.append(f"missing required reference: references/{module}/{filename}")

    files = package_files(root)
    resolved_root = root.resolve()
    allowed = {p.resolve() for p in files if not p.is_symlink()}
    for path in files:
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if parent != root):
            errors.append(f"not distributable: symbolic link at {relative}")
            continue
        if path.suffix.lower() in FORBIDDEN_EXTENSIONS or path.name.startswith(".env"):
            errors.append(f"not distributable: {relative}")
            continue
        if RAW_SOURCE_NAME.search(path.name):
            errors.append(f"raw source text: {relative}")
        if path.name == "SKILL.md" and path != skill:
            errors.append(f"nested skill entry: {relative}")
        if path.suffix.lower() not in TEXT_EXTENSIONS and not path.name.startswith("LICENSE"):
            continue
        text = path.read_text(encoding="utf-8")
        if PRIVATE_PATH.search(text):
            errors.append(f"private path: {relative}")
        if EMAIL.search(text):
            errors.append(f"email address: {relative}")
        if SECRET.search(text):
            errors.append(f"secret-like value: {relative}")
        if re.search(r"\[TODO:|\bTBD\b|PLACEHOLDER", text):
            errors.append(f"unfinished scaffold: {relative}")
        for target in LINK.findall(text):
            target = target.strip().strip("<>")
            if urlsplit(target).scheme or target.startswith("#"):
                continue
            clean_target = unquote(target.split("#", 1)[0])
            if not clean_target:
                continue
            destination = (path.parent / clean_target).resolve()
            if not destination.is_relative_to(resolved_root) or not destination.is_file():
                errors.append(f"broken link: {relative} -> {clean_target}")
            elif destination not in allowed:
                errors.append(f"link target not packaged: {relative} -> {clean_target}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--package", type=Path, help="write an installable ZIP after validation")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        errors = validate(root)
    except (OSError, UnicodeError) as error:
        print(f"ERROR: unreadable package input ({type(error).__name__})", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    files = package_files(root)
    if args.package:
        output = args.package.resolve()
        if output.suffix.lower() != ".zip" or (
            output.is_relative_to(root) and not output.is_relative_to(root / "dist")
        ):
            print("ERROR: unsafe archive output; repository archives belong in dist/", file=sys.stderr)
            return 1
        if output.exists() and not output.is_relative_to(root / "dist"):
            print("ERROR: existing external output will not be overwritten", file=sys.stderr)
            return 1
        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                archive.write(path, "dreamie-design/" + path.relative_to(root).as_posix())
        print(f"PACKAGED {len(files)} files: {output.name}")
    print(f"PASS: dreamie-design, {len(MODULES)} modules, {len(files)} distributable files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
