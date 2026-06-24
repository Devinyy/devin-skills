# Current Status

Last verified locally: 2026-06-24.

## Verified Channels

| Platform | Example Status | Output Type |
|---|---|---|
| Local file | Verified | audio/transcript metadata path |
| Bilibili | Verified | media, audio, transcript, summary |
| Douyin | Verified with cookies + Playwright fallback | media, audio, transcript, summary |
| Xiaohongshu | Verified | media, audio, transcript, note text, summary |
| WeChat article | Verified | article text, summary |
| WeChat Channels / 视频号 | Verified preview mode | preview text, metadata, summary |

## Current Capabilities

- Detects platform from URLs and share text.
- Extracts media where available.
- Normalizes audio to 16k mono WAV.
- Transcribes with `faster-whisper` or Apple Silicon `mlx`.
- Summarizes in three styles:
  - `dual`
  - `faithful`
  - `note`
- Runs batch jobs as a resumable sequential queue.
- Uses Playwright fallback for Douyin and WeChat Channels preview pages.
- Lists and cleans output directories.

## Known Limits

- WeChat Channels web previews often do not expose playable video streams.
- Douyin may require freshly exported cookies after captcha verification.
- WeChat article embedded video download remains best-effort; article text extraction is the stable path.
- Cloud deployment is not yet implemented.
- Feishu/Lark export is still an integration boundary, not a built-in command.

## Recommended Smoke Checks

```bash
bash scripts/check-env.sh
.venv/bin/python -m pytest -q
.venv/bin/python scripts/list-outputs.py outputs
```

## Packaging Notes

Do not package runtime artifacts:

- `.venv/`
- `outputs/`
- `.pytest_cache/`
- `__pycache__/`
- `tmp/`
- cookie files

