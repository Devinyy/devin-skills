# Output Format

## metadata.json

Contains source, platform, title, author, URL, local asset path, and extractor metadata.

Preview-only sources, such as some WeChat Channels web previews, include status fields:

```json
{
  "metadata": {
    "content_type": "preview",
    "availability": "preview_only",
    "media_status": "not_available",
    "media_reason": "..."
  }
}
```

## transcript.json

```json
{
  "language": "zh",
  "duration": 123.45,
  "segments": [
    {"start": 0.0, "end": 3.2, "text": "..."}
  ]
}
```

## transcript.md

Timestamped transcript.

## summary.md

Structured Markdown knowledge document. The default `dual` style contains:

- `A. 忠实摘要`
- `B. 可收藏笔记`

Use `--summary-style faithful` or `--summary-style note` to generate only one layer.

Summarization writes two Markdown files:

- `summary.md`: stable compatibility filename.
- `{主标题}.md`: title-based filename derived from the first `# ` heading, for human browsing and Obsidian-style note names.

When answering the user after a successful summarization, include the absolute `summary.md` path, the title-based Markdown path, and paste the full Markdown content. The path alone is not enough unless the user explicitly asks for paths only.

## Obsidian export

When a local Obsidian installation is detected, `summary.md` is copied into the selected vault under `Video Knowledge/` by default. Detection order:

1. `OBSIDIAN_VAULT_PATH`, if set and valid.
2. The open or most recent vault in `~/Library/Application Support/obsidian/obsidian.json`.

Use `OBSIDIAN_OUTPUT_DIR` to change the vault subdirectory, or `--no-obsidian` to disable export for a run. When export succeeds, `metadata.json` includes `obsidian_path`. Metadata also includes `summary_path` and `summary_named_path`.
