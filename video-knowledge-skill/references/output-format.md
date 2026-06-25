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

When a local Obsidian installation is detected, `summary.md` is copied into an automatically selected two-level category folder at the vault root by default, such as `研发/DevOps/标题.md` or `AI工程/Agent/标题.md`. The primary category is selected by an LLM from the fixed category list; if the model is unavailable, the exporter falls back to local keyword rules. The exported note also includes an `## Obsidian 关联` section with wiki links to flat topic notes under `主题/`, for example `主题/研发 SOP.md` or `主题/AI工程 Agent.md`. When an article spans domains, related categories are linked as additional topics so Obsidian graph view can show cross-domain relationships. Detection order:

1. `OBSIDIAN_VAULT_PATH`, if set and valid.
2. The open or most recent vault in `~/Library/Application Support/obsidian/obsidian.json`.

Use `OBSIDIAN_OUTPUT_DIR` to place category folders under a chosen vault subdirectory, `OBSIDIAN_CATEGORY` to force one category path for a run, `OBSIDIAN_CLASSIFIER=rules` to disable model classification, or `--no-obsidian` to disable export. When export succeeds, `metadata.json` includes `obsidian_path`, `obsidian_category`, `obsidian_category_method`, `obsidian_category_reason`, and `obsidian_related_categories`. Metadata also includes `summary_path` and `summary_named_path`.

Both `summary.md` and the title-based Markdown file include a final `## 原链接` section with the original input URL or local source path. Obsidian exports preserve this source block and append `## Obsidian 关联` after it.

Supported category paths:

- `研发/前端`, `研发/DevOps`, `研发/工程质量`, `研发/架构`, `研发/SOP`
- `AI工程/Agent`, `AI工程/Skill`, `AI工程/Harness`, `AI工程/AI Coding`
- `管理/团队协作`, `管理/流程治理`, `管理/CodeReview`
- `设计/产品设计`, `设计/UIUX`
- `生活/阅读`, `生活/摄影`, `生活/旅行`, `生活/杂谈`
