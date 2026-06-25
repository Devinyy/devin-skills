from __future__ import annotations

import json
import os
from pathlib import Path

import requests
from yt_dlp.utils import DownloadError

from .browser_utils import capture_browser_page, load_playwright_cookies
from .base import ExtractResult
from .yt_dlp_extractor import YtDlpExtractor, _task_id
from scripts.extract_audio import normalize_audio
from extractors.generic_article import _clean_text


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.douyin.com/",
}


class Extractor(YtDlpExtractor):
    platform = "douyin"

    def __init__(self):
        env_name = "DOUYIN_COOKIE_FILE"
        if "WECHAT" in env_name:
            env_name = "WECHAT_COOKIE_FILE"
        super().__init__(platform=self.platform, cookie_file=os.getenv(env_name))

    def extract(self, source: str, output_dir: Path) -> ExtractResult:
        try:
            return super().extract(source, output_dir)
        except DownloadError as exc:
            try:
                return self._extract_with_browser_fallback(source, output_dir)
            except Exception as fallback_exc:
                try:
                    return self._extract_with_jina_fallback(source, output_dir)
                except Exception as article_exc:
                    raise exc from article_exc

    def _extract_with_browser_fallback(self, source: str, output_dir: Path) -> ExtractResult:
        aweme = self._fetch_aweme_detail_with_browser(source)
        video = aweme.get("video") or {}
        play_addr = video.get("play_addr") or {}
        media_urls = play_addr.get("url_list") or []
        media_url = media_urls[0] if media_urls else None
        if not media_url:
            raise RuntimeError("Douyin browser fallback found no playable video URL")

        task_id = _task_id(source)
        task_dir = output_dir / task_id
        asset_dir = task_dir / "assets"
        asset_dir.mkdir(parents=True, exist_ok=True)

        source_media = asset_dir / "source.mp4"
        resp = requests.get(media_url, headers=HEADERS, stream=True, timeout=120)
        resp.raise_for_status()
        with source_media.open("wb") as fh:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    fh.write(chunk)

        audio_path = normalize_audio(source_media, asset_dir / "audio.wav")
        author = aweme.get("author") or {}
        title = aweme.get("desc") or aweme.get("item_title") or "抖音视频"
        aweme_id = aweme.get("aweme_id") or task_id
        webpage_url = f"https://www.douyin.com/video/{aweme_id}"

        return ExtractResult(
            platform=self.platform,
            source=source,
            task_id=task_id,
            title=title,
            author=author.get("nickname"),
            webpage_url=webpage_url,
            audio_path=str(audio_path),
            video_path=str(source_media),
            metadata={
                "id": aweme_id,
                "title": title,
                "description": aweme.get("desc"),
                "duration": (aweme.get("duration") or 0) / 1000,
                "uploader": author.get("nickname"),
                "webpage_url": webpage_url,
                "extractor": "douyin_browser_fallback",
            },
        )

    def _fetch_aweme_detail_with_browser(self, source: str) -> dict:
        cookies = load_playwright_cookies(self.cookie_file, ["douyin.com", "iesdouyin.com"])
        details: list[dict] = []

        def on_response(resp):
            if "aweme/v1/web/aweme/detail" not in resp.url:
                return
            try:
                payload = json.loads(resp.text())
            except Exception:
                return
            detail = payload.get("aweme_detail")
            if detail:
                details.append(detail)

        capture_browser_page(
            source,
            user_agent=HEADERS["User-Agent"],
            cookies=cookies,
            on_response=on_response,
            done=lambda: bool(details),
        )

        if not details:
            raise RuntimeError("Douyin browser fallback could not capture aweme detail JSON")
        return details[0]

    def _extract_with_jina_fallback(self, source: str, output_dir: Path) -> ExtractResult:
        markdown = self._fetch_jina_markdown(source)
        title = self._title_from_jina_markdown(markdown) or "抖音内容"
        task_id = _task_id(source)
        task_dir = output_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        article_markdown = self._render_jina_article(title, source, markdown)
        (task_dir / "article.md").write_text(article_markdown, encoding="utf-8")

        return ExtractResult(
            platform=self.platform,
            source=source,
            task_id=task_id,
            title=title,
            author=None,
            webpage_url=source,
            audio_path=None,
            video_path=None,
            metadata={
                "content_type": "douyin_page_text",
                "title": title,
                "webpage_url": source,
                "text_preview": markdown[:2000],
                "extractor": "douyin_jina_reader_fallback",
                "fallback_reason": "media_download_or_browser_detail_failed",
            },
        )

    def _fetch_jina_markdown(self, source: str) -> str:
        reader_url = f"https://r.jina.ai/http://{source}"
        resp = requests.get(reader_url, headers=HEADERS, timeout=60)
        resp.raise_for_status()
        text = resp.text.strip()
        if not text:
            raise RuntimeError("Jina reader returned empty Douyin content")
        return text

    def _title_from_jina_markdown(self, markdown: str) -> str | None:
        for line in markdown.splitlines():
            if line.startswith("Title:"):
                title = line.removeprefix("Title:").strip()
                return title or None
        return None

    def _render_jina_article(self, title: str, source: str, markdown: str) -> str:
        content = _clean_text(markdown)
        return (
            f"# {title}\n\n"
            f"原文：{source}\n\n"
            "## 正文\n\n"
            f"{content}\n"
        )
