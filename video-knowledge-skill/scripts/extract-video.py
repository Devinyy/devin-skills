#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.detect_platform import detect  # type: ignore
from extractors.local_file import LocalFileExtractor


def get_extractor(platform: str):
    if platform == "local_file":
        return LocalFileExtractor()
    if platform in {"bilibili", "douyin", "xiaohongshu", "wechat_article", "wechat_channels"}:
        module = importlib.import_module(f"extractors.{platform}")
        return module.Extractor()
    raise ValueError(f"Unsupported or unknown platform: {platform}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", default="outputs")
    parser.add_argument("--transcribe", action="store_true")
    parser.add_argument("--summarize", action="store_true")
    parser.add_argument("--model-size", default="small")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--transcribe-backend", choices=["faster-whisper", "mlx"], default="faster-whisper")
    parser.add_argument("--summary-style", choices=["dual", "faithful", "note"], default="dual")
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    detected = detect(args.input)
    extractor = get_extractor(detected["platform"])
    result = extractor.extract(detected["input"], output)

    task_dir = output / result.task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    (task_dir / "metadata.json").write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))

    if args.transcribe:
        if not result.audio_path:
            raise RuntimeError("No audio file generated; cannot transcribe.")
        subprocess.run([
            sys.executable,
            str(Path(__file__).with_name("transcribe.py")),
            result.audio_path,
            "--output-dir", str(task_dir),
            "--model-size", args.model_size,
            "--language", args.language,
            "--backend", args.transcribe_backend,
        ], check=True)

    if args.summarize:
        subprocess.run([
            sys.executable,
            str(Path(__file__).with_name("summarize.py")),
            str(task_dir),
            "--summary-style", args.summary_style,
        ], check=True)


if __name__ == "__main__":
    main()
