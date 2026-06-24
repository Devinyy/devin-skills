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
