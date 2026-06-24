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
