#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import requests
from openai import OpenAI
from dotenv import load_dotenv

DUAL_PROMPT = """
你是企业知识库整理助手。请根据视频字幕或文章内容生成“双层知识文档”。

第一层是忠实摘要，用于知识库归档和回溯原始内容；第二层是可收藏笔记，用于阅读、复盘和二次传播。
第二层允许适度重组、提炼标题和抽象框架，但不得新增原内容没有依据的事实，不得把推测写成事实。

输出 Markdown，必须使用以下结构和标题：

# 标题

## A. 忠实摘要

## 一句话总结

## 核心观点

## 时间线

## 关键知识点

## 我的思考

## B. 可收藏笔记

## 笔记标题

## 核心矛盾

## 方法框架

## 执行清单

## 适用边界

## 标签

要求：
- A 层必须尽量贴近原字幕、文章和元数据，保留时间线，明确标注字幕质量较差或识别不确定的地方。
- B 层可以把内容重组为更清晰、更有阅读价值的笔记，但所有概念、判断和建议都必须能从原内容推导出来。
- 如果 B 层有抽象概念，请尽量用原内容中的表达或可解释的改写，不要制造无法溯源的新理论。
- 中文输出。
"""

FAITHFUL_PROMPT = """
你是企业知识库整理助手。请根据视频字幕或文章内容生成忠实摘要，用于知识库归档和回溯原始内容。

输出 Markdown，必须使用以下结构和标题：

# 标题

## A. 忠实摘要

## 一句话总结

## 核心观点

## 时间线

## 关键知识点

## 我的思考

## 标签

要求：
- 尽量贴近原字幕、文章和元数据，保留时间线。
- 明确标注字幕质量较差或识别不确定的地方。
- 不要编造原内容没有的信息。
- 中文输出。
"""

NOTE_PROMPT = """
你是企业知识库整理助手。请根据视频字幕或文章内容生成可收藏笔记，用于阅读、复盘和二次传播。

输出 Markdown，必须使用以下结构和标题：

# 标题

## B. 可收藏笔记

## 笔记标题

## 核心矛盾

## 方法框架

## 执行清单

## 适用边界

## 标签

要求：
- 允许适度重组、提炼标题和抽象框架，但不得新增原内容没有依据的事实，不得把推测写成事实。
- 所有概念、判断和建议都必须能从原内容推导出来。
- 如果有抽象概念，请尽量用原内容中的表达或可解释的改写，不要制造无法溯源的新理论。
- 中文输出。
"""

PROMPTS = {
    "dual": DUAL_PROMPT,
    "faithful": FAITHFUL_PROMPT,
    "note": NOTE_PROMPT,
}

PROMPT = DUAL_PROMPT


def safe_filename(value: str, fallback: str) -> str:
    name = re.sub(r'[\\/:*?"<>|#^\[\]]+', " ", value).strip()
    name = re.sub(r"\s+", " ", name)
    name = name.rstrip(".")
    if not name:
        name = fallback
    return name[:100].strip() or fallback


def title_from_markdown(markdown: str) -> str | None:
    for line in markdown.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            return title or None
    return None


def write_summary_files(task: Path, summary: str) -> Path:
    summary_path = task / "summary.md"
    summary_path.write_text(summary, encoding="utf-8")

    title = title_from_markdown(summary)
    if not title:
        return summary_path

    named_path = task / f"{safe_filename(title, fallback=task.name)}.md"
    if named_path != summary_path:
        named_path.write_text(summary, encoding="utf-8")
    return named_path


def update_summary_metadata(task: Path, named_path: Path) -> None:
    metadata_path = task / "metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            metadata = {}
    else:
        metadata = {}
    metadata["summary_path"] = str(task / "summary.md")
    metadata["summary_named_path"] = str(named_path)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


def get_prompt(summary_style: str = "dual") -> str:
    try:
        return PROMPTS[summary_style]
    except KeyError as exc:
        raise ValueError(f"Unsupported summary style: {summary_style}") from exc


def summarize(task_dir: str, summary_style: str = "dual") -> str:
    load_dotenv()

    task = Path(task_dir)
    transcript_path = task / "transcript.md"
    article_path = task / "article.md"
    metadata_path = task / "metadata.json"
    content_blocks = []
    if transcript_path.exists():
        content_blocks.append(("字幕", transcript_path.read_text(encoding="utf-8")))
    if article_path.exists():
        label = "文章或笔记内容" if content_blocks else "内容"
        content_blocks.append((label, article_path.read_text(encoding="utf-8")))
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else {}

    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL") or None,
    )
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    source_content = "\n\n".join(
        f"{label}：\n{text[:60000]}" for label, text in content_blocks
    )
    content = f"元数据：\n{json.dumps(metadata, ensure_ascii=False, indent=2)}\n\n{source_content}"
    messages = [
        {"role": "system", "content": get_prompt(summary_style)},
        {"role": "user", "content": content},
    ]
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        summary = resp.choices[0].message.content or ""
    except Exception:
        summary = summarize_with_http_fallback(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            model=model,
            messages=messages,
        )
    named_path = write_summary_files(task, summary)
    update_summary_metadata(task, named_path)
    return summary


def summarize_with_http_fallback(api_key: str | None, base_url: str | None, model: str, messages: list[dict]) -> str:
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for summary generation.")
    if not base_url:
        raise RuntimeError("OPENAI_BASE_URL is required for HTTP fallback summary generation.")

    endpoint = base_url.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint = f"{endpoint}/chat/completions"

    resp = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": messages,
        },
        timeout=120,
    )
    resp.raise_for_status()
    payload = json.loads(resp.content.decode("utf-8"))
    return payload["choices"][0]["message"]["content"] or ""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_dir")
    parser.add_argument("--summary-style", choices=sorted(PROMPTS), default="dual")
    args = parser.parse_args()
    print(summarize(args.task_dir, summary_style=args.summary_style))


if __name__ == "__main__":
    main()
