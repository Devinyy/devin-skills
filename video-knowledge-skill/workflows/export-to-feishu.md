# Export to Feishu/Lark Workflow

## Goal

Save `summary.md`, `transcript.md`, and metadata into a Feishu/Lark knowledge base.

## Recommended Document Structure

```md
# {video_title}

## Source
- Platform: {platform}
- URL: {source_url}
- Author: {author}

## Summary
{summary}

## Transcript
{transcript}
```

## Implementation Note

This package leaves Feishu export as an integration boundary. In the user's environment, connect it through `lark-mcp` or `lark-cli`.
