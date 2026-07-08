# video-knowledge-skill

A self-hosted skill for extracting knowledge from mainstream video links and local video/audio files.

Chinese skill document: `SKILL.zh.md`.

## Scope

Supported targets:

- Bilibili
- Douyin
- Xiaohongshu
- WeChat article video
- WeChat Channels / 视频号, with local-file fallback
- Local video/audio files

## Install

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
```

Install ffmpeg separately:

```bash
brew install ffmpeg
```

## Configure

```bash
cp .env.example .env
```

Add API keys and optional cookie file paths.

## Check Environment

```bash
bash scripts/check-env.sh
```

## Extract One Video

```bash
.venv/bin/python scripts/extract-video.py "<url-or-file>" --output outputs
.venv/bin/python scripts/extract-video.py "<url-or-file>" --output outputs --transcribe --summarize
.venv/bin/python scripts/extract-video.py "<url-or-file>" --output outputs --transcribe --summarize \
  --transcribe-backend mlx --model-size small --language zh --summary-style dual
```

On Apple Silicon Macs, use `--transcribe-backend mlx` to run Whisper through MLX/Metal GPU acceleration.
Summary styles are `dual` (default), `faithful`, and `note`.

## Batch Extract

```bash
.venv/bin/python scripts/batch-extract.py inputs.txt --output outputs --transcribe --summarize \
  --transcribe-backend mlx --model-size small --language zh
.venv/bin/python scripts/batch-extract.py inputs.txt --output outputs --resume
```

Batch mode runs as a sequential queue and writes state to `outputs/batch-queue.json`.
Use `--resume` to skip completed items after an interruption, and `--retry-failed` to retry failed items.

## Output

```txt
outputs/{task_id}/
├── metadata.json
├── transcript.json
├── transcript.md
├── transcript.srt
├── summary.md
└── assets/
    └── audio.wav
```

List generated outputs:

```bash
.venv/bin/python scripts/list-outputs.py outputs
```

Remove empty output directories:

```bash
.venv/bin/python scripts/clean-empty-outputs.py outputs
```

## Notes

- Bilibili and local files are the most stable.
- Extractors normalize audio to 16k mono WAV before transcription.
- Transcription supports `faster-whisper` and Apple Silicon `mlx` backends.
- Douyin supports yt-dlp first and Playwright browser fallback; fresh cookies may still be required.
- Xiaohongshu extracts both video/audio and note text when available.
- WeChat article links can be summarized as articles even when no embedded video is available.
- WeChat Channels direct video download is best-effort only. Preview-only pages are rejected instead of summarized, because title/metadata-only notes pollute the knowledge base.
