# Batch Video Extract Workflow

## Input File

Create `inputs.txt`:

```txt
https://www.bilibili.com/video/xxx
https://www.douyin.com/video/xxx
/path/to/local-video.mp4
```

## Command

```bash
python scripts/batch-extract.py inputs.txt --output outputs --transcribe --summarize \
  --transcribe-backend mlx --model-size small --language zh --summary-style dual
```

Resume after interruption:

```bash
python scripts/batch-extract.py inputs.txt --output outputs --resume
```

Retry failed queue items:

```bash
python scripts/batch-extract.py inputs.txt --output outputs --resume --retry-failed
```

## Notes

- Batch mode runs as a sequential queue and stores state in `outputs/batch-queue.json`.
- One failed link does not stop later links.
- Review failed tasks manually or retry them with `--resume --retry-failed`.
- For restricted platforms, provide cookies or local files.
- Use `scripts/list-outputs.py outputs` to inspect generated tasks.
- Use `scripts/clean-empty-outputs.py outputs` to remove empty output directories.
