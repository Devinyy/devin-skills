#!/usr/bin/env bash
set -e

echo "Checking video-knowledge-skill environment..."

check_cmd() {
  if command -v "$1" >/dev/null 2>&1; then
    echo "[OK] $1: $(command -v $1)"
  else
    echo "[MISS] $1 is not installed"
  fi
}

PYTHON_BIN="${PYTHON:-}"
if [ -z "$PYTHON_BIN" ]; then
  if [ -x ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN=python
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
  fi
fi

if [ -z "$PYTHON_BIN" ]; then
  echo "[MISS] no python interpreter available"
  exit 0
fi

echo "[OK] python interpreter: $PYTHON_BIN"
check_cmd ffmpeg

if command -v yt-dlp >/dev/null 2>&1; then
  echo "[OK] yt-dlp CLI: $(command -v yt-dlp)"
elif "$PYTHON_BIN" -m yt_dlp --version >/dev/null 2>&1; then
  echo "[OK] yt-dlp python module: $("$PYTHON_BIN" -m yt_dlp --version)"
else
  echo "[MISS] yt-dlp is not installed"
fi

"$PYTHON_BIN" - <<'PY'
modules = ["yt_dlp", "faster_whisper", "mlx_whisper", "requests", "bs4", "pydantic", "openai", "playwright"]
for m in modules:
    try:
        __import__(m)
        print(f"[OK] python module: {m}")
    except Exception:
        print(f"[MISS] python module: {m}")
PY

"$PYTHON_BIN" - <<'PY'
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        browser.close()
    print("[OK] playwright chromium browser")
except Exception as exc:
    print(f"[MISS] playwright chromium browser: {exc}")
    print("       Install with: python -m playwright install chromium")
PY

echo "Done."
