from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import requests
from yt_dlp.utils import DownloadError

from .browser_utils import capture_browser_page
from .base import ExtractResult, InsufficientContentError
from .yt_dlp_extractor import YtDlpExtractor, _task_id
from scripts.extract_audio import normalize_audio


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://channels.weixin.qq.com/",
}


class Extractor(YtDlpExtractor):
    platform = "wechat_channels"

    def __init__(self):
        env_name = "WECHAT_CHANNELS_COOKIE_FILE"
        if "WECHAT" in env_name:
            env_name = "WECHAT_COOKIE_FILE"
        super().__init__(platform=self.platform, cookie_file=os.getenv(env_name))

    def extract(self, source: str, output_dir: Path) -> ExtractResult:
        try:
            return super().extract(source, output_dir)
        except DownloadError as exc:
            try:
                return self._extract_with_browser_fallback(source, output_dir)
            except InsufficientContentError:
                shutil.rmtree(output_dir / _task_id(source), ignore_errors=True)
                raise
            except Exception as fallback_exc:
                raise exc from fallback_exc

    def _extract_with_browser_fallback(self, source: str, output_dir: Path) -> ExtractResult:
        payload, media_url = self._fetch_feed_info_and_media_url_with_browser(source)
        data = payload.get("data") or {}
        author = data.get("authorInfo") or {}
        feed = data.get("feedInfo") or {}
        title = feed.get("description") or "微信视频号"

        if not media_url:
            raise InsufficientContentError(
                "WeChat Channels preview exposed only title/metadata and no playable media; "
                "refusing to generate a placeholder note."
            )

        task_id = _task_id(source)
        task_dir = output_dir / task_id
        asset_dir = task_dir / "assets"
        task_dir.mkdir(parents=True, exist_ok=True)

        asset_dir.mkdir(parents=True, exist_ok=True)
        source_media = asset_dir / "source.mp4"
        resp = requests.get(media_url, headers=HEADERS, stream=True, timeout=120)
        resp.raise_for_status()
        with source_media.open("wb") as fh:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)

        audio_path = normalize_audio(source_media, asset_dir / "audio.wav")

        return ExtractResult(
            platform=self.platform,
            source=source,
            task_id=task_id,
            title=title,
            author=author.get("nickname"),
            webpage_url=source,
            audio_path=str(audio_path),
            video_path=str(source_media),
            metadata={
                "title": title,
                "availability": "media_available",
                "media_status": "downloaded",
                "description": feed.get("description"),
                "uploader": author.get("nickname"),
                "create_time": feed.get("createtime"),
                "webpage_url": source,
                "extractor": "wechat_channels_browser_fallback",
            },
        )

    def _fetch_feed_info_and_media_url_with_browser(self, source: str) -> tuple[dict, str]:
        payloads: list[dict] = []
        media_urls: list[str] = []

        def on_response(resp):
            url = resp.url
            if "/api/feed/get_feed_info" in url:
                try:
                    payloads.append(json.loads(resp.text()))
                except Exception:
                    pass
            content_type = resp.headers.get("content-type") or ""
            if "finder.video.qq.com" in url and "stodownload" in url and content_type.startswith("video/"):
                media_urls.append(url)

        capture_browser_page(
            source,
            user_agent=HEADERS["User-Agent"],
            on_response=on_response,
            done=lambda: bool(payloads and media_urls),
        )

        if not payloads:
            raise RuntimeError("WeChat Channels fallback could not capture feed info JSON")
        if not media_urls:
            return payloads[0], None
        return payloads[0], media_urls[0]
