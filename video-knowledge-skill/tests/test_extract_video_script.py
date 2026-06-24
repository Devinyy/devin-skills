import runpy
import sys
from types import SimpleNamespace

from extractors.base import ExtractResult


def test_extract_video_passes_detected_input_to_extractor(tmp_path, monkeypatch):
    seen = {}

    class FakeExtractor:
        def extract(self, source, output_dir):
            seen["source"] = source
            return ExtractResult(
                platform="douyin",
                source=source,
                task_id="task123",
                title="标题",
                author=None,
                webpage_url=source,
                audio_path=None,
                video_path=None,
                metadata={},
            )

    monkeypatch.setattr(
        "scripts.detect_platform.detect",
        lambda value: {"platform": "douyin", "input": "https://v.douyin.com/TaD2t8lWUH0/", "confidence": 0.95},
    )
    monkeypatch.setattr(
        "importlib.import_module",
        lambda name: SimpleNamespace(Extractor=FakeExtractor),
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["extract-video.py", "分享文本 https://v.douyin.com/TaD2t8lWUH0/ 02/16", "--output", str(tmp_path)],
    )

    runpy.run_path("scripts/extract-video.py", run_name="__main__")

    assert seen["source"] == "https://v.douyin.com/TaD2t8lWUH0/"
