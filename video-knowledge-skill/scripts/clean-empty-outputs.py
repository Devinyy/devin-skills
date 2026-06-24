#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", nargs="?", default="outputs")
    args = parser.parse_args()

    root = Path(args.output_dir)
    removed = 0
    for child in sorted(root.iterdir() if root.exists() else []):
        if not child.is_dir():
            continue
        try:
            next(child.iterdir())
        except StopIteration:
            child.rmdir()
            removed += 1
            print(f"removed {child}")
    print(f"removed_empty_dirs={removed}")


if __name__ == "__main__":
    main()
