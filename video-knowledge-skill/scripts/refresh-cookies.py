#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.cookie_refresh import PLATFORM_CONFIG, refresh_cookies


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("platform", choices=sorted(PLATFORM_CONFIG), help="Platform cookie set to refresh.")
    parser.add_argument("--output", help="Cookie file path. Defaults to platform env var or local default.")
    parser.add_argument("--browser", help="Browser name accepted by yt-dlp, e.g. chrome, chromium, edge.")
    args = parser.parse_args()

    output = Path(args.output).expanduser() if args.output else None
    refreshed = refresh_cookies(args.platform, output=output, browser=args.browser, cwd=Path.cwd())
    print(str(refreshed))


if __name__ == "__main__":
    main()
