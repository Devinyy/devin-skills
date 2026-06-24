from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class ExtractResult:
    platform: str
    source: str
    task_id: str
    title: Optional[str]
    author: Optional[str]
    webpage_url: Optional[str]
    audio_path: Optional[str]
    video_path: Optional[str]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BaseExtractor:
    platform = "base"

    @classmethod
    def match(cls, source: str) -> bool:
        return False

    def extract(self, source: str, output_dir: Path) -> ExtractResult:
        raise NotImplementedError
