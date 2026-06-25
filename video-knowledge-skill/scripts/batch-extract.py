#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_sources(input_file: Path) -> list[str]:
    lines = [line.strip() for line in input_file.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line and not line.startswith("#")]


def queue_path(output: Path, queue_state: str | None) -> Path:
    return Path(queue_state) if queue_state else output / "batch-queue.json"


def build_queue(input_file: Path, sources: list[str], existing: dict | None = None) -> dict:
    existing_items = {
        item["source"]: item
        for item in (existing or {}).get("items", [])
        if item.get("source")
    }
    items = []
    for source in sources:
        previous = existing_items.get(source)
        if previous:
            item = dict(previous)
            if item.get("status") == "running":
                item["status"] = "pending"
            items.append(item)
        else:
            items.append(
                {
                    "source": source,
                    "status": "pending",
                    "attempts": 0,
                    "returncode": None,
                    "updated_at": None,
                }
            )
    return {
        "input_file": str(input_file),
        "updated_at": now_iso(),
        "items": items,
    }


def load_queue(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_queue(path: Path, queue: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    queue["updated_at"] = now_iso()
    path.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")


def should_process(item: dict, resume: bool, retry_failed: bool) -> bool:
    status = item.get("status")
    if not resume:
        return True
    if status == "done":
        return False
    if status == "failed" and not retry_failed:
        return False
    return True


def build_command(args: argparse.Namespace, source: str) -> list[str]:
    script = Path(__file__).with_name("extract-video.py")
    cmd = [sys.executable, str(script), source, "--output", args.output]
    if args.transcribe:
        cmd.append("--transcribe")
    if args.summarize:
        cmd.append("--summarize")
    if args.no_obsidian:
        cmd.append("--no-obsidian")
    cmd.extend(["--model-size", args.model_size])
    cmd.extend(["--language", args.language])
    cmd.extend(["--transcribe-backend", args.transcribe_backend])
    cmd.extend(["--summary-style", args.summary_style])
    return cmd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="Text file, one URL or local path per line")
    parser.add_argument("--output", default="outputs")
    parser.add_argument("--transcribe", action="store_true")
    parser.add_argument("--summarize", action="store_true")
    parser.add_argument("--model-size", default="small")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--transcribe-backend", choices=["faster-whisper", "mlx"], default="faster-whisper")
    parser.add_argument("--summary-style", choices=["dual", "faithful", "note"], default="dual")
    parser.add_argument("--no-obsidian", action="store_true", help="Do not auto-copy summary.md into a detected Obsidian vault.")
    parser.add_argument("--queue-state", help="Path to queue state JSON. Defaults to <output>/batch-queue.json")
    parser.add_argument("--resume", action="store_true", help="Resume queue, skipping completed items")
    parser.add_argument("--retry-failed", action="store_true", help="With --resume, retry failed items")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    input_file = Path(args.input_file)
    sources = read_sources(input_file)
    state_path = queue_path(output, args.queue_state)
    existing = load_queue(state_path) if args.resume else None
    queue = build_queue(input_file, sources, existing=existing)
    save_queue(state_path, queue)

    failures = 0
    for item in queue["items"]:
        if not should_process(item, resume=args.resume, retry_failed=args.retry_failed):
            print(f"\n=== Skipping {item['status']}: {item['source']} ===")
            continue

        item["status"] = "running"
        item["attempts"] = int(item.get("attempts") or 0) + 1
        item["updated_at"] = now_iso()
        save_queue(state_path, queue)

        print(f"\n=== Processing: {item['source']} ===")
        result = subprocess.run(build_command(args, item["source"]), check=False)
        item["returncode"] = result.returncode
        item["status"] = "done" if result.returncode == 0 else "failed"
        item["updated_at"] = now_iso()
        save_queue(state_path, queue)

        if result.returncode != 0:
            failures += 1

    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
