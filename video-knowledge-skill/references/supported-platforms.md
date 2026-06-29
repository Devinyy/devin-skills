# Supported Platforms

## Capability Matrix

| Platform | Detect | Media Download | Transcript | Text/Article Capture | Summary | Notes |
|---|---:|---:|---:|---:|---:|---|
| Local files | Yes | N/A | Yes | N/A | Yes | Most stable path for manually exported videos. |
| Bilibili | Yes | Yes | Yes | Metadata only | Yes | Uses yt-dlp first, then public API fallback for common WBI/playurl failures. |
| Douyin | Yes | Yes | Yes | Metadata only | Yes | Uses yt-dlp first, then Playwright browser fallback; fresh cookies may be required. |
| Xiaohongshu | Yes | Yes | Yes | Note text | Yes | yt-dlp works for tested links; note description is also saved as `article.md`. |
| WeChat article | Yes | Best-effort embedded media | If media exists | Article body | Yes | Article-only links still produce `article.md` and `summary.md`. |
| WeChat Channels / 视频号 | Yes | Best-effort only | If media is exposed | No placeholder notes | No when preview-only | Public web preview often exposes only preview text and metadata; preview-only pages are rejected. |
| Generic article | Yes | No | No | Main text | Yes | Best-effort extraction for public web articles such as cnblogs.com posts. |

## Platform Details

### Bilibili

- Preferred: yt-dlp.
- Fallback: public Bilibili view/playurl APIs.
- Cookie: optional, useful for restricted/private/high-quality cases.
- Reliability: high.

### Douyin

- Preferred: yt-dlp.
- Fallback: Playwright browser session that captures runtime `aweme_detail` and playable media URLs.
- Cookie: often required. Export a fresh Netscape cookie file after passing web verification.
- Reliability: medium.

### Xiaohongshu

- Preferred: yt-dlp for media.
- Text capture: note title and description are rendered to `article.md` when available.
- Cookie: optional, may be needed for restricted links.
- Reliability: medium.

### WeChat Article

- Preferred: parse article HTML.
- Text capture: `#js_content` becomes `article.md`.
- Embedded media: best-effort only.
- Reliability: medium for articles, lower for embedded media.

### WeChat Channels / 视频号

- Preferred: browser media capture.
- Text capture: preview description and author are only diagnostic metadata, not enough for a note.
- Media download: best-effort only. Many web preview pages show "scan in WeChat" and do not expose playable streams.
- Preview-only pages fail with a clear error and do not create `summary.md` or Obsidian notes.
- Local fallback: manually exported video or screen recording.
- Reliability: low for direct media.

### Generic Article

- Preferred: parse common article containers such as `article`, `main`, `#cnblogs_post_body`, and `.entry-content`.
- Text capture: title, author, source URL, and main body become `article.md`.
- Media download: not attempted.
- Reliability: medium; heavily scripted or login-restricted pages may need a custom extractor or copied article text.

### Local Files

- Preferred: ffmpeg normalization to 16k mono WAV, then transcription.
- Reliability: high.
