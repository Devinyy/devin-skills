# Video Knowledge Core Chain Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring `video-knowledge-skill` to the Phase 1 handoff acceptance target: local files and Bilibili can produce metadata, normalized audio, transcript, and summary through one stable command.

**Architecture:** Keep platform decisions out of the main workflow. `scripts/detect_platform.py` detects the platform, `scripts/extract-video.py` loads the matching extractor, extractors return a normalized `ExtractResult`, and dedicated scripts handle audio normalization, ASR, and LLM summary.

**Tech Stack:** Python 3, yt-dlp, ffmpeg, faster-whisper, OpenAI-compatible chat completions, pytest.

---

## File Structure

- Modify: `extractors/base.py`
  - Add a concrete `match()` contract and document the stable `ExtractResult` fields.
- Modify: `extractors/local_file.py`
  - Use the shared audio normalizer instead of embedding ffmpeg details.
- Modify: `extractors/yt_dlp_extractor.py`
  - Download media through yt-dlp, then normalize final audio to 16k mono wav.
- Modify: `extractors/bilibili.py`
  - Keep Bilibili as a thin yt-dlp extractor with cookie support.
- Create: `scripts/extract_audio.py`
  - Shared Python module for ffmpeg audio normalization.
- Create: `scripts/extract-audio.py`
  - CLI wrapper that writes `audio.wav` or a requested output path.
- Modify: `scripts/extract-video.py`
  - Ensure extraction result writes exactly one `metadata.json` under `outputs/{task_id}/`.
- Modify: `scripts/transcribe.py`
  - Add SRT output and keep `transcript.json` and `transcript.md`.
- Modify: `scripts/summarize.py`
  - Align summary prompt to the handoff's required Markdown headings.
- Modify: `scripts/check-env.sh`
  - Check the new `extract-audio.py` path and key Python modules.
- Create: `tests/test_detect_platform.py`
- Create: `tests/test_extract_audio.py`
- Create: `tests/test_transcript_outputs.py`
- Create: `tests/test_summary_prompt.py`
- Modify: `requirements.txt`
  - Add `pytest`.
- Modify: `README.md`
  - Align commands and output shape with the implemented Phase 1 chain.

---

### Task 1: Add Baseline Tests For Platform Detection

**Files:**
- Create: `tests/test_detect_platform.py`

- [ ] **Step 1: Write failing tests**

```python
from scripts.detect_platform import detect


def test_detects_bilibili_domains():
    assert detect("https://www.bilibili.com/video/BV1xx411c7mD")["platform"] == "bilibili"
    assert detect("https://b23.tv/abc123")["platform"] == "bilibili"


def test_detects_phase_two_and_wechat_domains():
    assert detect("https://www.douyin.com/video/123")["platform"] == "douyin"
    assert detect("https://xhslink.com/a/b")["platform"] == "xiaohongshu"
    assert detect("https://mp.weixin.qq.com/s/example")["platform"] == "wechat_article"
    assert detect("https://channels.weixin.qq.com/platform/post/123")["platform"] == "wechat_channels"


def test_detects_local_file_by_existing_path(tmp_path):
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"not a real video")
    assert detect(str(video))["platform"] == "local_file"
```

- [ ] **Step 2: Run test to verify current behavior**

Run:

```bash
python -m pytest tests/test_detect_platform.py -v
```

Expected: PASS. If `pytest` is missing, add it in Task 8 before rerunning.

- [ ] **Step 3: Commit**

```bash
git add tests/test_detect_platform.py
git commit -m "test: cover platform detection"
```

---

### Task 2: Introduce Shared Audio Normalization

**Files:**
- Create: `scripts/extract_audio.py`
- Create: `scripts/extract-audio.py`
- Create: `tests/test_extract_audio.py`

- [ ] **Step 1: Write failing tests**

```python
from pathlib import Path
from unittest.mock import patch

from scripts.extract_audio import normalize_audio


def test_normalize_audio_invokes_ffmpeg_for_16k_mono_wav(tmp_path):
    source = tmp_path / "input.mp4"
    output = tmp_path / "audio.wav"
    source.write_bytes(b"placeholder")

    with patch("scripts.extract_audio.subprocess.run") as run:
        result = normalize_audio(source, output)

    assert result == output
    run.assert_called_once_with(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(source),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            str(output),
        ],
        check=True,
    )
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_extract_audio.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'scripts.extract_audio'`.

- [ ] **Step 3: Implement shared module and CLI**

```python
# scripts/extract_audio.py
from __future__ import annotations

import subprocess
from pathlib import Path


def normalize_audio(source: str | Path, output: str | Path) -> Path:
    src = Path(source).expanduser().resolve()
    out = Path(output).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-f",
            "wav",
            str(out),
        ],
        check=True,
    )
    return out
```

```python
# scripts/extract-audio.py
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from extract_audio import normalize_audio


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(normalize_audio(Path(args.input), Path(args.output)))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

```bash
python -m pytest tests/test_extract_audio.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/extract_audio.py scripts/extract-audio.py tests/test_extract_audio.py
git commit -m "feat: add shared audio normalization"
```

---

### Task 3: Normalize Extractor Audio Outputs

**Files:**
- Modify: `extractors/local_file.py`
- Modify: `extractors/yt_dlp_extractor.py`
- Modify: `extractors/base.py`

- [ ] **Step 1: Update `BaseExtractor` contract**

Add this method to `BaseExtractor`:

```python
    @classmethod
    def match(cls, source: str) -> bool:
        return False
```

- [ ] **Step 2: Update local file extractor**

Replace embedded ffmpeg invocation with:

```python
from scripts.extract_audio import normalize_audio
```

and:

```python
audio_path = normalize_audio(src, asset_dir / "audio.wav")
```

- [ ] **Step 3: Update yt-dlp extractor**

Download source media to `asset_dir / "source.%(ext)s"`, then normalize the first downloaded candidate into `asset_dir / "audio.wav"` using `normalize_audio`.

- [ ] **Step 4: Run focused smoke checks**

```bash
python scripts/detect-platform.py test.mp4
python -m pytest tests/test_extract_audio.py tests/test_detect_platform.py -v
```

Expected: platform detection returns `local_file`; tests PASS.

- [ ] **Step 5: Commit**

```bash
git add extractors/base.py extractors/local_file.py extractors/yt_dlp_extractor.py
git commit -m "feat: normalize extractor audio output"
```

---

### Task 4: Add Transcript SRT Output

**Files:**
- Modify: `scripts/transcribe.py`
- Create: `tests/test_transcript_outputs.py`

- [ ] **Step 1: Write formatting tests for SRT helper**

```python
from scripts.transcribe import format_srt_timestamp, render_srt


def test_format_srt_timestamp():
    assert format_srt_timestamp(65.432) == "00:01:05,432"


def test_render_srt_segments():
    segments = [{"start": 0.0, "end": 1.5, "text": "你好"}]
    assert render_srt(segments) == "1\n00:00:00,000 --> 00:00:01,500\n你好\n"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_transcript_outputs.py -v
```

Expected: FAIL because helper functions do not exist.

- [ ] **Step 3: Implement helpers and write `transcript.srt`**

Add:

```python
def format_srt_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def render_srt(segments: list[dict]) -> str:
    blocks = []
    for index, segment in enumerate(segments, start=1):
        blocks.append(
            f"{index}\n"
            f"{format_srt_timestamp(segment['start'])} --> {format_srt_timestamp(segment['end'])}\n"
            f"{segment['text']}\n"
        )
    return "\n".join(blocks)
```

After writing `transcript.md`, also write:

```python
(out / "transcript.srt").write_text(render_srt(result_segments), encoding="utf-8")
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_transcript_outputs.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/transcribe.py tests/test_transcript_outputs.py
git commit -m "feat: write transcript srt output"
```

---

### Task 5: Align Summary Markdown Contract

**Files:**
- Modify: `scripts/summarize.py`
- Create: `tests/test_summary_prompt.py`

- [ ] **Step 1: Write prompt contract test**

```python
from scripts.summarize import PROMPT


def test_summary_prompt_contains_required_handoff_headings():
    for heading in [
        "## 一句话总结",
        "## 核心观点",
        "## 时间线",
        "## 关键知识点",
        "## 我的思考",
        "## 标签",
    ]:
        assert heading in PROMPT
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_summary_prompt.py -v
```

Expected: FAIL for missing exact headings.

- [ ] **Step 3: Update `PROMPT`**

Make `PROMPT` require this exact Markdown structure:

```markdown
# 标题

## 一句话总结

## 核心观点

## 时间线

## 关键知识点

## 我的思考

## 标签
```

- [ ] **Step 4: Run test**

```bash
python -m pytest tests/test_summary_prompt.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/summarize.py tests/test_summary_prompt.py
git commit -m "feat: align summary markdown contract"
```

---

### Task 6: Verify End-To-End Local File Flow

**Files:**
- No code changes expected.

- [ ] **Step 1: Generate a tiny local test video**

```bash
mkdir -p tmp
ffmpeg -y -f lavfi -i sine=frequency=1000:duration=1 -f lavfi -i color=c=black:s=320x180:d=1 -shortest tmp/sample.mp4
```

- [ ] **Step 2: Run extraction**

```bash
python scripts/extract-video.py tmp/sample.mp4 --output outputs
```

Expected: JSON prints with `"platform": "local_file"` and a non-empty `"audio_path"`.

- [ ] **Step 3: Verify output files**

```bash
find outputs -maxdepth 3 -type f | sort
```

Expected: one task directory containing `metadata.json` and `assets/audio.wav`.

- [ ] **Step 4: Commit only if fixes were needed**

```bash
git status --short
```

Expected: no source changes from this task.

---

### Task 7: Verify Bilibili Public Video Flow

**Files:**
- Modify only if verification exposes a defect.

- [ ] **Step 1: Run a public Bilibili extraction**

```bash
python scripts/extract-video.py "https://www.bilibili.com/video/BV1xx411c7mD" --output outputs
```

Expected: JSON prints with `"platform": "bilibili"` and `assets/audio.wav`.

- [ ] **Step 2: Retry with cookies if required**

```bash
BILIBILI_COOKIE_FILE=/absolute/path/to/cookies.txt python scripts/extract-video.py "https://www.bilibili.com/video/BV1xx411c7mD" --output outputs
```

Expected: same output shape. If cookie-protected access fails, document it as an input/auth issue, not a core-chain failure.

- [ ] **Step 3: Commit only if fixes were needed**

```bash
git status --short
```

Expected: no source changes from this task.

---

### Task 8: Update Environment And Documentation

**Files:**
- Modify: `requirements.txt`
- Modify: `scripts/check-env.sh`
- Modify: `README.md`

- [ ] **Step 1: Add test dependency**

Add:

```txt
pytest>=8.0.0
```

- [ ] **Step 2: Update environment check**

Ensure `scripts/check-env.sh` checks:

```bash
check_cmd python
check_cmd ffmpeg
check_cmd yt-dlp
```

and Python modules:

```python
modules = ["yt_dlp", "faster_whisper", "requests", "bs4", "pydantic", "openai"]
```

- [ ] **Step 3: Update README Phase 1 commands**

Document:

```bash
python scripts/extract-video.py "<url-or-file>" --output outputs
python scripts/extract-video.py "<url-or-file>" --output outputs --transcribe --summarize
```

and output:

```txt
outputs/{task_id}/
├── metadata.json
├── transcript.json
├── transcript.md
├── transcript.srt
├── summary.md
└── assets/audio.wav
```

- [ ] **Step 4: Run docs-adjacent checks**

```bash
bash scripts/check-env.sh
python -m pytest -v
```

Expected: environment script reports installed/missing dependencies clearly; pytest PASS.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt scripts/check-env.sh README.md
git commit -m "docs: document phase one video workflow"
```

---

### Task 9: Phase 2 Planning Gate

**Files:**
- Modify after Phase 1 is green: `extractors/douyin.py`, `extractors/xiaohongshu.py`, platform-specific tests.

- [ ] **Step 1: Confirm Phase 1 acceptance**

```bash
python -m pytest -v
bash scripts/check-env.sh
python scripts/extract-video.py tmp/sample.mp4 --output outputs
```

Expected: tests PASS, env check runs, local extraction writes metadata and audio.

- [ ] **Step 2: Decide Phase 2 scope**

Document whether Phase 2 starts with Douyin first or Xiaohongshu first. Recommended order: Douyin, then Xiaohongshu, because Douyin can keep the yt-dlp-first strategy while Xiaohongshu more often needs custom normalization and cookies.

- [ ] **Step 3: Create a new plan for Phase 2**

Create:

```txt
docs/superpowers/plans/2026-06-23-video-knowledge-douyin-xiaohongshu.md
```

Expected: separate plan with extractor fallback behavior, cookie handling, and public-link verification cases.

---

## Self-Review

- Spec coverage: Phase 1 covers local file, Bilibili, metadata output, normalized audio, transcript generation, Markdown summary format, and batch-compatible command shape. Phase 2 and WeChat/Lark work are intentionally gated after Phase 1.
- Placeholder scan: No implementation step uses TBD/TODO wording. The only future item is a named Phase 2 planning gate with a concrete output plan path.
- Type consistency: The plan keeps the existing `ExtractResult` fields and `extract(source: str, output_dir: Path) -> ExtractResult` signature.

## Execution Choice

Plan complete and saved to `docs/superpowers/plans/2026-06-23-video-knowledge-core-chain.md`.

1. **Subagent-Driven (recommended)** - dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** - execute tasks in this session using executing-plans, batch execution with checkpoints.
