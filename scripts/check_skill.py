#!/usr/bin/env python3
"""Offline checks for this instruction package, not for literature evidence.

This is a deliberately small checker, not a full YAML or Markdown parser.
It does not fetch URLs, execute examples, alter files, inspect scientific
claims, or validate review-corpus schemas.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


LINK = re.compile(r"\[[^\]\n]*\]\(([^)\n]+)\)")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
PUNCTUATION = {"\u2014", "\u2013", "\u201c", "\u201d"}


def frontmatter(text: str) -> tuple[dict[str, str], list[str], int]:
    """Read single-line top-level fields needed by this package."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, ["SKILL.md: missing opening frontmatter delimiter"], 0
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, ["SKILL.md: missing closing frontmatter delimiter"], 0
    values: dict[str, str] = {}
    errors: list[str] = []
    for number, line in enumerate(lines[1:end], 2):
        match = re.match(r"^([a-z][a-z-]*):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.groups()
        if key in values:
            errors.append(f"SKILL.md:{number}: duplicate top-level field {key}")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values, errors, end + 1


def prose_lines(text: str):
    """Yield non-fenced lines and report an unclosed fence at EOF.

    Skip frontmatter and quoted blocks for punctuation checks. Inline code,
    link destinations, and simple numeric ranges are protected separately.
    Manual review is still needed for other verbatim scientific notation.
    """
    lines = text.splitlines()
    start = 0
    if lines and lines[0] == "---":
        try:
            start = lines.index("---", 1) + 1
        except ValueError:
            start = len(lines)
    active: tuple[str, int, int] | None = None
    for number, line in enumerate(lines[start:], start + 1):
        fence = FENCE.match(line)
        if active:
            if fence and fence[1][0] == active[0] and len(fence[1]) >= active[1] and not fence[2].strip():
                active = None
            continue
        if fence:
            active = (fence[1][0], len(fence[1]), number)
            continue
        if not line.lstrip().startswith(">"):
            yield number, line, False
    if active:
        yield active[2], "", True


INLINE_CODE = re.compile(r"`+[^`]*`+")


def prose_without_inline_code(line: str) -> str:
    """Remove inline code spans before other protected-content substitutions."""
    return INLINE_CODE.sub("", line)


def check_skill(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    if not root.is_dir():
        return [f"Not a skill directory: {root}"]
    for required in ("SKILL.md", "README.md"):
        if not (root / required).is_file():
            errors.append(f"Missing {required}")
    skill_path = root / "SKILL.md"
    if skill_path.is_file():
        fields, field_errors, _ = frontmatter(skill_path.read_text(encoding="utf-8"))
        errors.extend(field_errors)
        name = fields.get("name", "")
        if not NAME.fullmatch(name) or len(name) > 64:
            errors.append("SKILL.md: invalid or missing name")
        elif name != root.name:
            errors.append("SKILL.md: name must match the package directory for portability")
        description = fields.get("description", "")
        if not description or len(description) > 1024 or description in {"|", ">", "|-", ">-"}:
            errors.append("SKILL.md: expected a nonempty single-line description of at most 1024 characters")

    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", "__pycache__"} for part in path.relative_to(root).parts):
            continue
        relative = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        for number, line, unclosed in prose_lines(text):
            if unclosed:
                errors.append(f"{relative}:{number}: unclosed code fence")
                continue
            scan_line = prose_without_inline_code(line)
            for match in LINK.finditer(scan_line):
                target = match[1].strip()
                target = target.split(' "', 1)[0].strip("<>")
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                target_path = Path(unquote(parsed.path))
                if target_path.is_absolute():
                    errors.append(f"{relative}:{number}: nonportable absolute local link: {target}")
                    continue
                resolved = (path.parent / target_path).resolve()
                try:
                    resolved.relative_to(root)
                except ValueError:
                    errors.append(f"{relative}:{number}: local link escapes package: {target}")
                    continue
                if not resolved.exists():
                    errors.append(f"{relative}:{number}: missing local target: {target}")
            prose = re.sub(r"\]\([^)]+\)", "]", scan_line)
            prose = re.sub(r"(?<=\d)\u2013(?=\d)", "-", prose)
            if any(char in prose for char in PUNCTUATION):
                errors.append(f"{relative}:{number}: review dash or typographic quote in editable prose")
            if line.rstrip() != line:
                errors.append(f"{relative}:{number}: trailing whitespace")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    errors = check_skill(args.directory)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("Package checks passed. Scientific judgments, corpus integrity, external URLs, and live workflows were not validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
