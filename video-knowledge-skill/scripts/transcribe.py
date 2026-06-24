#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from faster_whisper import WhisperModel
import mlx_whisper


MLX_MODEL_REPOS = {
    "tiny": "mlx-community/whisper-tiny",
    "base": "mlx-community/whisper-base-mlx",
    "small": "mlx-community/whisper-small-mlx",
    "medium": "mlx-community/whisper-medium-mlx",
    "large": "mlx-community/whisper-large-mlx",
    "large-v2": "mlx-community/whisper-large-v2-mlx",
    "large-v3": "mlx-community/whisper-large-v3-mlx",
}


def format_srt_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def render_srt(segments: list[dict]) -> str:
    blocks = []
    for index, segment in enumerate(segments, start=1):
        blocks.append(
            f"{index}\n"
            f"{format_srt_timestamp(segment['start'])} --> {format_srt_timestamp(segment['end'])}\n"
            f"{segment['text']}\n"
        )
    return "\n".join(blocks)


def mlx_model_name(model_size: str) -> str:
    if "/" in model_size:
        return model_size
    return MLX_MODEL_REPOS.get(model_size, f"mlx-community/whisper-{model_size}-mlx")


def transcribe(audio_path: str, output_dir: str, model_size: str = "small", language: str = "zh", backend: str = "faster-whisper") -> dict:
    audio = Path(audio_path)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    if backend == "mlx":
        payload = transcribe_with_mlx(str(audio), model_size=model_size, language=language)
    elif backend == "faster-whisper":
        payload = transcribe_with_faster_whisper(str(audio), model_size=model_size, language=language)
    else:
        raise ValueError(f"Unsupported transcription backend: {backend}")

    write_transcript_outputs(payload, out)
    return payload


def transcribe_with_faster_whisper(audio_path: str, model_size: str, language: str) -> dict:
    model = WhisperModel(model_size, device="auto", compute_type="auto")
    segments, info = model.transcribe(audio_path, language=language, vad_filter=True)
    result_segments = []
    for seg in segments:
        result_segments.append({"start": seg.start, "end": seg.end, "text": seg.text.strip()})
    return {
        "backend": "faster-whisper",
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": info.duration,
        "segments": result_segments,
    }


def transcribe_with_mlx(audio_path: str, model_size: str, language: str) -> dict:
    result = mlx_whisper.transcribe(
        audio_path,
        path_or_hf_repo=mlx_model_name(model_size),
        language=language,
        verbose=False,
    )
    result_segments = []
    for seg in result.get("segments", []):
        text = str(seg.get("text", "")).strip()
        if text:
            result_segments.append({"start": float(seg["start"]), "end": float(seg["end"]), "text": text})
    duration = result_segments[-1]["end"] if result_segments else 0
    return {
        "backend": "mlx",
        "language": result.get("language") or language,
        "language_probability": None,
        "duration": duration,
        "segments": result_segments,
    }


def write_transcript_outputs(payload: dict, out: Path) -> None:
    lines = [
        f"[{seg['start']:.2f} - {seg['end']:.2f}] {seg['text']}"
        for seg in payload["segments"]
    ]
    (out / "transcript.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "transcript.md").write_text("\n".join(lines), encoding="utf-8")
    (out / "transcript.srt").write_text(render_srt(payload["segments"]), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("audio_path")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--model-size", default="small")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--backend", choices=["faster-whisper", "mlx"], default="faster-whisper")
    args = parser.parse_args()
    transcribe(args.audio_path, args.output_dir, args.model_size, args.language, args.backend)


if __name__ == "__main__":
    main()
