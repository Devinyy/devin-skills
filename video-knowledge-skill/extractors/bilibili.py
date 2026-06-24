from __future__ import annotations

import re
import os
from pathlib import Path

import requests
from yt_dlp.utils import DownloadError

from .base import ExtractResult
from .yt_dlp_extractor import YtDlpExtractor, _task_id
from scripts.extract_audio import normalize_audio


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.bilibili.com/",
}


def _extract_bvid(source: str) -> str:
    match = re.search(r"(BV[a-zA-Z0-9]+)", source)
    if not match:
        raise ValueError(f"Cannot find Bilibili BV id in URL: {source}")
    return match.group(1)


class Extractor(YtDlpExtractor):
    platform = "bilibili"

    def __init__(self):
        env_name = "BILIBILI_COOKIE_FILE"
        if "WECHAT" in env_name:
            env_name = "WECHAT_COOKIE_FILE"
        super().__init__(platform=self.platform, cookie_file=os.getenv(env_name))

    def extract(self, source: str, output_dir: Path) -> ExtractResult:
        try:
            return super().extract(source, output_dir)
        except DownloadError as exc:
            try:
                return self._extract_with_public_api(source, output_dir)
            except Exception as fallback_exc:
                raise exc from fallback_exc

    def _extract_with_public_api(self, source: str, output_dir: Path) -> ExtractResult:
        bvid = _extract_bvid(source)
        task_id = _task_id(source)
        task_dir = output_dir / task_id
        asset_dir = task_dir / "assets"
        asset_dir.mkdir(parents=True, exist_ok=True)

        session = requests.Session()
        session.headers.update(HEADERS)

        view_resp = session.get(
            "https://api.bilibili.com/x/web-interface/view",
            params={"bvid": bvid},
            timeout=30,
        )
        view_resp.raise_for_status()
        view_payload = view_resp.json()
        if view_payload.get("code") != 0:
            raise RuntimeError(f"Bilibili view API failed: {view_payload.get('message')}")

        info = view_payload["data"]
        cid = info["pages"][0]["cid"] if info.get("pages") else info["cid"]

        play_resp = session.get(
            "https://api.bilibili.com/x/player/playurl",
            params={"bvid": bvid, "cid": cid, "fnval": 16, "qn": 64, "fourk": 1},
            headers={**HEADERS, "Referer": f"https://www.bilibili.com/video/{bvid}/"},
            timeout=30,
        )
        play_resp.raise_for_status()
        play_payload = play_resp.json()
        if play_payload.get("code") != 0:
            raise RuntimeError(f"Bilibili playurl API failed: {play_payload.get('message')}")

        audios = play_payload.get("data", {}).get("dash", {}).get("audio") or []
        if not audios:
            raise RuntimeError("Bilibili playurl API returned no DASH audio streams")

        audio = max(audios, key=lambda item: item.get("bandwidth") or 0)
        audio_url = audio.get("baseUrl") or audio.get("base_url")
        if not audio_url:
            raise RuntimeError("Bilibili DASH audio stream has no URL")

        source_media = asset_dir / "source.m4s"
        media_resp = session.get(
            audio_url,
            headers={**HEADERS, "Referer": f"https://www.bilibili.com/video/{bvid}/"},
            stream=True,
            timeout=60,
        )
        media_resp.raise_for_status()
        with source_media.open("wb") as fh:
            for chunk in media_resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)

        audio_path = normalize_audio(source_media, asset_dir / "audio.wav")
        owner = info.get("owner") or {}

        return ExtractResult(
            platform=self.platform,
            source=source,
            task_id=task_id,
            title=info.get("title"),
            author=owner.get("name"),
            webpage_url=f"https://www.bilibili.com/video/{bvid}/",
            audio_path=str(audio_path),
            video_path=None,
            metadata={
                "id": info.get("aid"),
                "bvid": info.get("bvid") or bvid,
                "cid": cid,
                "title": info.get("title"),
                "description": info.get("desc"),
                "duration": info.get("duration"),
                "uploader": owner.get("name"),
                "webpage_url": f"https://www.bilibili.com/video/{bvid}/",
                "extractor": "bilibili_public_api",
            },
        )
