from __future__ import annotations

import hashlib
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .base import BaseExtractor, ExtractResult


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
}


def _task_id(source: str) -> str:
    return hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]


def parse_article(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title_node = soup.select_one("#activity-name")
    author_node = soup.select_one("#js_name")
    content_node = soup.select_one("#js_content")
    meta_title = soup.select_one('meta[property="og:title"]')

    title = ""
    if title_node:
        title = " ".join(title_node.get_text(" ", strip=True).split())
    elif meta_title and meta_title.get("content"):
        title = meta_title["content"].strip()

    author = " ".join(author_node.get_text(" ", strip=True).split()) if author_node else ""
    text = " ".join(content_node.get_text(" ", strip=True).split()) if content_node else ""

    return {"title": title, "author": author, "text": text}


def render_article_markdown(article: dict, source: str) -> str:
    lines = [
        f"# {article['title'] or '微信文章'}",
        "",
    ]
    if article.get("author"):
        lines.extend([f"作者：{article['author']}", ""])
    lines.extend([f"原文：{source}", ""])
    if article.get("text"):
        lines.extend(["## 正文", "", article["text"], ""])
    return "\n".join(lines).rstrip() + "\n"


def find_embedded_video_urls(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    content = soup.select_one("#js_content")
    if not content:
        return []

    urls = []
    for tag in content.find_all(["video", "iframe"]):
        src = tag.get("src") or tag.get("data-src")
        if src:
            urls.append(src)
    return urls


class Extractor(BaseExtractor):
    platform = "wechat_article"

    def extract(self, source: str, output_dir: Path) -> ExtractResult:
        task_id = _task_id(source)
        task_dir = output_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        resp = requests.get(source, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        html = resp.content.decode(resp.encoding or "utf-8", errors="ignore")

        article = parse_article(html)
        video_urls = find_embedded_video_urls(html)
        metadata = {
            "content_type": "article",
            "title": article["title"],
            "author": article["author"],
            "webpage_url": source,
            "text_preview": article["text"][:2000],
            "embedded_video_urls": video_urls,
        }
        result = ExtractResult(
            platform=self.platform,
            source=source,
            task_id=task_id,
            title=article["title"],
            author=article["author"],
            webpage_url=source,
            audio_path=None,
            video_path=None,
            metadata=metadata,
        )

        (task_dir / "metadata.json").write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        (task_dir / "article.md").write_text(render_article_markdown(article, source), encoding="utf-8")

        return result
