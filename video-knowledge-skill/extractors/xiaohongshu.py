from __future__ import annotations

import os
from pathlib import Path

from .base import ExtractResult
from .yt_dlp_extractor import YtDlpExtractor


def render_note_markdown(result: ExtractResult) -> str:
    title = result.title or result.metadata.get("title") or "小红书笔记"
    description = result.metadata.get("description") or ""
    lines = [
        f"# {title}",
        "",
        f"来源：{result.webpage_url or result.source}",
        "",
    ]
    if result.author:
        lines.extend([f"作者：{result.author}", ""])
    if description:
        lines.extend(["## 正文", "", description.strip(), ""])
    return "\n".join(lines)


class Extractor(YtDlpExtractor):
    platform = "xiaohongshu"

    def __init__(self):
        env_name = "XIAOHONGSHU_COOKIE_FILE"
        if "WECHAT" in env_name:
            env_name = "WECHAT_COOKIE_FILE"
        super().__init__(platform=self.platform, cookie_file=os.getenv(env_name))

    def extract(self, source: str, output_dir: Path) -> ExtractResult:
        result = super().extract(source, output_dir)
        if result.metadata.get("description"):
            task_dir = output_dir / result.task_id
            task_dir.mkdir(parents=True, exist_ok=True)
            (task_dir / "article.md").write_text(render_note_markdown(result), encoding="utf-8")
        return result
