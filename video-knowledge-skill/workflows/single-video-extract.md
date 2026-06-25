# Single Video Extract Workflow

## Goal

Convert one video link or local video/audio file into a structured knowledge document.

## Steps

1. Detect platform with `scripts/detect-platform.py`.
2. Route to platform extractor.
3. Download or extract audio.
4. Save `metadata.json`.
5. Run `mlx` or `faster-whisper` to generate transcript when media is available.
6. Run LLM summarization to generate `summary.md`; default summary style is `dual`.
7. Optionally export to Feishu/Lark.

## Command

```bash
python scripts/extract-video.py "<url-or-file>" --output outputs --transcribe --summarize \
  --transcribe-backend mlx --model-size small --language zh --summary-style dual
```

Use `--summary-style faithful` for archive-only summaries, or `--summary-style note` for a concise reusable note.

By default, after `summary.md` is generated, the workflow auto-detects a local Obsidian vault and copies the note into a two-level category folder at the vault root, such as `研发/DevOps/` or `AI工程/Agent/`. The note also links to topic notes under `主题/` so Obsidian graph view can connect primary and related categories. Use `--no-obsidian` to disable this behavior.

## Output

```txt
outputs/{task_id}/
├── metadata.json
├── transcript.json
├── transcript.md
├── transcript.srt
├── summary.md
├── {主标题}.md
└── assets/
```

Article-only or preview-only links may produce `article.md` and `summary.md` without transcript files.

`summary.md` and `{主标题}.md` include `## 原链接` with the original URL or local source path.

## User Response

When summarization succeeds, respond with:

- `summary.md` absolute path.
- Title-based Markdown path, derived from the first `# ` heading.
- Obsidian note path, when a local Obsidian vault is detected.
- The full contents of `summary.md`.

Do not make the user ask a second time for the output.
