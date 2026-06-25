---
name: video-knowledge-skill
description: Use when extracting, transcribing, summarizing, or making reusable notes from Bilibili, Douyin, Xiaohongshu, WeChat article, WeChat Channels, local video, or local audio sources.
---

# Video Knowledge Skill

## Purpose

This skill extracts knowledge from mainstream video links or local video/audio files, then converts them into structured notes that can be saved to a knowledge base such as Feishu/Lark.

Primary goal:

> Video link / local video → metadata → audio → transcript → structured summary → Markdown / Feishu document

## Supported Inputs

- Bilibili video links
- Douyin video links
- Xiaohongshu note/video links
- WeChat article links containing embedded video
- WeChat Channels / 视频号 links or manually exported video files
- Local video/audio files

## Reliability Policy

Different platforms have different anti-crawling and login restrictions. This skill must not promise full automation for every link.

| Platform | Preferred Strategy | Reliability |
|---|---|---|
| Bilibili | yt-dlp first, optional cookies | High |
| Douyin | yt-dlp first, Playwright browser fallback, optional cookies | Medium |
| Xiaohongshu | yt-dlp first, note text capture, optional cookies | Medium |
| WeChat article | article parser first, embedded media best-effort | Medium |
| WeChat Channels | web preview parser, media best-effort, local upload fallback | Medium-Low |
| Local file | ffmpeg + faster-whisper | High |

## Intent Routing

Use this skill when the user asks to:

- summarize a video
- extract subtitles/transcript from a video
- convert a video into notes
- extract key points from Bilibili/Douyin/Xiaohongshu/WeChat video links
- batch process video links
- save video knowledge into Feishu/Lark

## Workflows

### Single video extraction

Use `workflows/single-video-extract.md`.

### Batch video extraction

Use `workflows/batch-video-extract.md`.

### Transcript-only extraction

Use `workflows/transcript-extract.md`.

### Feishu/Lark export

Use `workflows/export-to-feishu.md`.

## Execution Contract

The skill should produce the following files for each video:

```txt
outputs/{task_id}/
├── metadata.json
├── transcript.json
├── transcript.md
├── summary.md
└── assets/
```

If a local Obsidian vault is detected, `summary.md` is also copied into the vault under `Video Knowledge/` by default. Set `OBSIDIAN_VAULT_PATH` to choose a vault, `OBSIDIAN_OUTPUT_DIR` to choose the subdirectory, or pass `--no-obsidian` to skip export.

## Final Response Contract

After a successful extraction with summarization, the agent must return:

1. The absolute path to `outputs/{task_id}/summary.md`.
2. The Obsidian note path when export succeeds.
3. The full Markdown content of `summary.md`.

Do not only say that the summary was generated. If the user asks for "输出", "结果", "笔记", or similar wording, read `summary.md` from disk and paste its content in the response, with the path above it.

For batch processing, return the queue status plus each successful task's `summary.md` absolute path. If the user asks for content, include the full `summary.md` content for each requested task.

## Core Commands

Check environment:

```bash
bash scripts/check-env.sh
```

This checks ffmpeg, Python modules, and Playwright Chromium availability.

Detect platform:

```bash
python scripts/detect-platform.py "<url-or-file>"
```

Extract one video:

```bash
python scripts/extract-video.py "<url-or-file>" --output outputs
python scripts/extract-video.py "<url-or-file>" --output outputs --transcribe --summarize --transcribe-backend mlx --model-size small --summary-style dual
```

Batch extract:

```bash
python scripts/batch-extract.py inputs.txt --output outputs --transcribe --summarize --transcribe-backend mlx --model-size small
python scripts/batch-extract.py inputs.txt --output outputs --resume
```

Inspect and clean outputs:

```bash
python scripts/list-outputs.py outputs
python scripts/clean-empty-outputs.py outputs
```

## Boundaries

- Do not bypass paywalls or private-access restrictions.
- Do not extract content from private accounts without authorization.
- Prefer official APIs or user-provided exported files when platform restrictions exist.
- For WeChat Channels, direct video download is best-effort; preview text and metadata extraction should still produce article-style notes.
