#!/usr/bin/env python3
"""Estimate context size for files, directories, or stdin.

The estimate is intentionally simple and dependency-free. It is meant for
triage decisions, not billing-grade token accounting.
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import sys
from dataclasses import dataclass
from pathlib import Path


DEFAULT_IGNORES = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".next",
    ".nuxt",
    ".turbo",
    ".vercel",
    "node_modules",
    "bower_components",
    "vendor",
    "dist",
    "build",
    "coverage",
    "target",
    "__pycache__",
}

BINARY_SUFFIXES = {
    ".7z",
    ".avif",
    ".bin",
    ".bmp",
    ".class",
    ".dmg",
    ".doc",
    ".docx",
    ".exe",
    ".gif",
    ".ico",
    ".jar",
    ".jpeg",
    ".jpg",
    ".lockb",
    ".mov",
    ".mp3",
    ".mp4",
    ".o",
    ".pdf",
    ".png",
    ".ppt",
    ".pptx",
    ".pyc",
    ".so",
    ".sqlite",
    ".tar",
    ".webp",
    ".woff",
    ".woff2",
    ".xls",
    ".xlsx",
    ".zip",
}


@dataclass(frozen=True)
class FileEstimate:
    path: Path
    bytes_size: int
    tokens: int


def estimate_tokens(text: str) -> int:
    """Use a conservative chars/4 estimate with a small floor for non-empty text."""
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def is_ignored(path: Path, extra_excludes: tuple[str, ...]) -> bool:
    parts = set(path.parts)
    if parts & DEFAULT_IGNORES:
        return True
    path_text = str(path)
    return any(fnmatch.fnmatch(path.name, pattern) or pattern in path_text for pattern in extra_excludes)


def include_file(path: Path, include_patterns: tuple[str, ...]) -> bool:
    if not include_patterns:
        return True
    return any(fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(str(path), pattern) for pattern in include_patterns)


def looks_binary(path: Path) -> bool:
    return path.suffix.lower() in BINARY_SUFFIXES


def iter_files(paths: list[Path], include_patterns: tuple[str, ...], extra_excludes: tuple[str, ...]):
    for raw_path in paths:
        path = raw_path.expanduser()
        if not path.exists():
            print(f"warning: missing path skipped: {path}", file=sys.stderr)
            continue
        if path.is_file():
            if not looks_binary(path) and include_file(path, include_patterns) and not is_ignored(path, extra_excludes):
                yield path
            continue
        for root, dirs, files in os.walk(path):
            root_path = Path(root)
            dirs[:] = sorted(d for d in dirs if not is_ignored(root_path / d, extra_excludes))
            for file_name in sorted(files):
                file_path = root_path / file_name
                if looks_binary(file_path):
                    continue
                if is_ignored(file_path, extra_excludes):
                    continue
                if include_file(file_path, include_patterns):
                    yield file_path


def estimate_file(path: Path) -> FileEstimate | None:
    try:
        data = path.read_bytes()
    except OSError as exc:
        print(f"warning: could not read {path}: {exc}", file=sys.stderr)
        return None
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("utf-8", errors="ignore")
    return FileEstimate(path=path, bytes_size=len(data), tokens=estimate_tokens(text))


def format_int(value: int) -> str:
    return f"{value:,}"


def read_plan(total_tokens: int, file_count: int) -> str:
    if total_tokens <= 2_000:
        return "safe to read directly if relevant"
    if total_tokens <= 12_000:
        return "read targeted files or snippets; avoid rereading"
    if total_tokens <= 50_000:
        return "map and grep first; summarize large files before loading"
    if file_count > 100:
        return "inventory first; select a subsystem before opening files"
    return "too large for blind reading; require a narrower question or staged capsule"


def print_report(estimates: list[FileEstimate], top: int) -> None:
    total_tokens = sum(item.tokens for item in estimates)
    total_bytes = sum(item.bytes_size for item in estimates)
    print("Context estimate")
    print(f"- Files: {format_int(len(estimates))}")
    print(f"- Bytes: {format_int(total_bytes)}")
    print(f"- Estimated tokens: {format_int(total_tokens)}")
    print(f"- Read plan: {read_plan(total_tokens, len(estimates))}")
    if not estimates:
        return
    print()
    print(f"Top {min(top, len(estimates))} largest files:")
    for item in sorted(estimates, key=lambda entry: entry.tokens, reverse=True)[:top]:
        print(f"{format_int(item.tokens):>10} tokens  {item.path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Estimate context tokens for files, directories, or stdin.")
    parser.add_argument("paths", nargs="*", type=Path, help="Files or directories to estimate.")
    parser.add_argument("--stdin", action="store_true", help="Estimate text from stdin.")
    parser.add_argument("--top", type=int, default=10, help="Number of largest files to show.")
    parser.add_argument("--include", action="append", default=[], help="Include glob pattern; may repeat.")
    parser.add_argument("--exclude", action="append", default=[], help="Extra exclude pattern or path fragment; may repeat.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.stdin:
        text = sys.stdin.read()
        tokens = estimate_tokens(text)
        print("Context estimate")
        print("- Source: stdin")
        print(f"- Characters: {format_int(len(text))}")
        print(f"- Estimated tokens: {format_int(tokens)}")
        print(f"- Read plan: {read_plan(tokens, 1)}")
        return 0

    paths = args.paths or [Path(".")]
    estimates = [
        estimate
        for estimate in (
            estimate_file(path)
            for path in iter_files(paths, tuple(args.include), tuple(args.exclude))
        )
        if estimate is not None
    ]
    print_report(estimates, max(0, args.top))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
