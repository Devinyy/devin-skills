from __future__ import annotations

import hashlib
from pathlib import Path

from .base import BaseExtractor, ExtractResult
from scripts.extract_audio import normalize_audio


def _task_id(source: str) -> str:
    return hashlib.sha1(str(source).encode("utf-8")).hexdigest()[:12]


class LocalFileExtractor(BaseExtractor):
    platform = "local_file"

    def extract(self, source: str, output_dir: Path) -> ExtractResult:
        task_id = _task_id(source)
        task_dir = output_dir / task_id
        asset_dir = task_dir / "assets"
        asset_dir.mkdir(parents=True, exist_ok=True)

        src = Path(source).expanduser().resolve()
        if not src.exists():
            raise FileNotFoundError(f"Local file not found: {src}")

        audio_path = normalize_audio(src, asset_dir / "audio.wav")

        return ExtractResult(
            platform=self.platform,
            source=str(src),
            task_id=task_id,
            title=src.stem,
            author=None,
            webpage_url=None,
            audio_path=str(audio_path),
            video_path=str(src),
            metadata={"filename": src.name, "suffix": src.suffix},
        )
