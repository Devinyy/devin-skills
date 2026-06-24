#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", nargs="?", default="outputs")
    args = parser.parse_args()

    root = Path(args.output_dir)
    print("task_id\tplatform\tcontent_type\ttitle")
    for metadata_path in sorted(root.glob("*/metadata.json")):
        task_id = metadata_path.parent.name
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        platform = metadata.get("platform") or ""
        title = metadata.get("title") or metadata.get("metadata", {}).get("title") or ""
        content_type = metadata.get("metadata", {}).get("content_type") or "video"
        print(f"{task_id}\t{platform}\t{content_type}\t{title}")


if __name__ == "__main__":
    main()
