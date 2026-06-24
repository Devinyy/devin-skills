from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Optional

import yt_dlp

from .base import BaseExtractor, ExtractResult
from scripts.extract_audio import normalize_audio


def _task_id(source: str) -> str:
    return hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]


class YtDlpExtractor(BaseExtractor):
    platform = "yt_dlp"

    def __init__(self, platform: str, cookie_file: Optional[str] = None):
        self.platform = platform
        self.cookie_file = cookie_file

    def extract(self, source: str, output_dir: Path) -> ExtractResult:
        task_id = _task_id(source)
        task_dir = output_dir / task_id
        asset_dir = task_dir / "assets"
        asset_dir.mkdir(parents=True, exist_ok=True)

        outtmpl = str(asset_dir / "source.%(ext)s")
        options = {
            "outtmpl": outtmpl,
            "format": "bestaudio/best",
            "noplaylist": True,
            "quiet": False,
        }
        if self.cookie_file:
            options["cookiefile"] = self.cookie_file

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(source, download=True)

        candidates = sorted(asset_dir.glob("source.*"))
        source_media = candidates[0] if candidates else None
        audio_path = normalize_audio(source_media, asset_dir / "audio.wav") if source_media else None

        return ExtractResult(
            platform=self.platform,
            source=source,
            task_id=task_id,
            title=info.get("title"),
            author=info.get("uploader") or info.get("channel") or info.get("creator"),
            webpage_url=info.get("webpage_url") or source,
            audio_path=str(audio_path) if audio_path else None,
            video_path=None,
            metadata={
                "id": info.get("id"),
                "title": info.get("title"),
                "description": info.get("description"),
                "duration": info.get("duration"),
                "upload_date": info.get("upload_date"),
                "uploader": info.get("uploader"),
                "webpage_url": info.get("webpage_url"),
                "extractor": info.get("extractor"),
            },
        )
