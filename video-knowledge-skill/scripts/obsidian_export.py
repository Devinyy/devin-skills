#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path


DEFAULT_SUBDIR = "Video Knowledge"


def obsidian_config_path() -> Path:
    override = os.getenv("OBSIDIAN_CONFIG_PATH")
    if override:
        return Path(override).expanduser()
    return Path.home() / "Library" / "Application Support" / "obsidian" / "obsidian.json"


def detect_vault(config_path: Path | None = None) -> Path | None:
    env_path = os.getenv("OBSIDIAN_VAULT_PATH")
    if env_path:
        vault = Path(env_path).expanduser()
        return vault if vault.exists() and vault.is_dir() else None

    config = config_path or obsidian_config_path()
    if not config.exists():
        return None

    try:
        payload = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    vaults = payload.get("vaults") or {}
    candidates = []
    for item in vaults.values():
        path = item.get("path")
        if not path:
            continue
        vault = Path(path).expanduser()
        if vault.exists() and vault.is_dir():
            candidates.append((bool(item.get("open")), int(item.get("ts") or 0), vault))

    if not candidates:
        return None

    candidates.sort(key=lambda row: (row[0], row[1]), reverse=True)
    return candidates[0][2]


def safe_filename(value: str, fallback: str) -> str:
    name = re.sub(r'[\\/:*?"<>|#^\[\]]+', " ", value).strip()
    name = re.sub(r"\s+", " ", name)
    name = name.rstrip(".")
    if not name:
        name = fallback
    return name[:100].strip() or fallback


def title_from_summary(summary_path: Path) -> str | None:
    try:
        for line in summary_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        return None
    return None


def metadata_title(task_dir: Path) -> str | None:
    metadata_path = task_dir / "metadata.json"
    if not metadata_path.exists():
        return None
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    title = payload.get("title")
    return title.strip() if isinstance(title, str) and title.strip() else None


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    for index in range(2, 1000):
        candidate = path.with_name(f"{stem} {index}{suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Cannot find unique Obsidian output path for {path}")


def export_summary(task_dir: Path, vault: Path | None = None, subdir: str | None = None) -> Path | None:
    summary_path = task_dir / "summary.md"
    if not summary_path.exists():
        return None

    target_vault = vault or detect_vault()
    if not target_vault:
        return None

    target_subdir = subdir or os.getenv("OBSIDIAN_OUTPUT_DIR") or DEFAULT_SUBDIR
    target_dir = target_vault / target_subdir
    target_dir.mkdir(parents=True, exist_ok=True)

    title = title_from_summary(summary_path) or metadata_title(task_dir) or task_dir.name
    filename = safe_filename(title, fallback=task_dir.name)
    target_path = unique_path(target_dir / f"{filename}.md")
    shutil.copyfile(summary_path, target_path)
    return target_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_dir")
    parser.add_argument("--vault", help="Obsidian vault path. Defaults to auto-detected open/recent vault.")
    parser.add_argument("--subdir", help=f"Vault subdirectory. Defaults to {DEFAULT_SUBDIR!r}.")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser() if args.vault else None
    exported = export_summary(Path(args.task_dir), vault=vault, subdir=args.subdir)
    if exported:
        print(str(exported))


if __name__ == "__main__":
    main()
