from __future__ import annotations

import hashlib
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .base import BaseExtractor, ExtractResult
from .wechat_article import HEADERS


ARTICLE_SELECTORS = [
    "article",
    "#cnblogs_post_body",
    ".postBody",
    ".post",
    ".entry-content",
    ".article-content",
    ".markdown-body",
    "main",
]

REMOVE_SELECTORS = [
    "script",
    "style",
    "noscript",
    "nav",
    "header",
    "footer",
    "aside",
    ".comment",
    ".comments",
    "#comment_form",
    "#blog_post_info_block",
]


def _task_id(source: str) -> str:
    return hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]


def _clean_text(value: str) -> str:
    return "\n".join(line.strip() for line in value.splitlines() if line.strip())


def _meta_content(soup: BeautifulSoup, *names: str) -> str:
    for name in names:
        node = soup.select_one(f'meta[property="{name}"], meta[name="{name}"]')
        if node and node.get("content"):
            return node["content"].strip()
    return ""


def parse_article(html: str, source: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    for selector in REMOVE_SELECTORS:
        for node in soup.select(selector):
            node.decompose()

    title = _meta_content(soup, "og:title", "twitter:title")
    if not title and soup.title:
        title = soup.title.get_text(" ", strip=True)
    title = title.replace(" - 博客园", "").strip()

    author = _meta_content(soup, "author", "article:author")
    if not author:
        author_node = soup.select_one("#Header1_HeaderTitle, .postDesc a, .author, .post-author")
        author = author_node.get_text(" ", strip=True) if author_node else ""

    content_node = None
    for selector in ARTICLE_SELECTORS:
        content_node = soup.select_one(selector)
        if content_node and len(content_node.get_text(" ", strip=True)) > 100:
            break
    if not content_node:
        content_node = soup.body or soup

    text = _clean_text(content_node.get_text("\n", strip=True))
    return {"title": title, "author": author, "text": text, "source": source}


def render_article_markdown(article: dict) -> str:
    lines = [f"# {article['title'] or '网页文章'}", ""]
    if article.get("author"):
        lines.extend([f"作者：{article['author']}", ""])
    lines.extend([f"原文：{article['source']}", ""])
    if article.get("text"):
        lines.extend(["## 正文", "", article["text"], ""])
    return "\n".join(lines).rstrip() + "\n"


class Extractor(BaseExtractor):
    platform = "generic_article"

    def extract(self, source: str, output_dir: Path) -> ExtractResult:
        task_id = _task_id(source)
        task_dir = output_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        resp = requests.get(source, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        html = resp.content.decode(resp.encoding or "utf-8", errors="ignore")
        article = parse_article(html, source)

        metadata = {
            "content_type": "article",
            "title": article["title"],
            "author": article["author"],
            "webpage_url": source,
            "text_preview": article["text"][:2000],
            "extractor": self.platform,
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
        (task_dir / "article.md").write_text(render_article_markdown(article), encoding="utf-8")
        return result
