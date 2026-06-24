#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from extract_audio import normalize_audio


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(normalize_audio(Path(args.input), Path(args.output)))


if __name__ == "__main__":
    main()
