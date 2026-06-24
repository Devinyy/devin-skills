from unittest.mock import patch

from extractors.base import ExtractResult
from extractors.xiaohongshu import Extractor


def test_xiaohongshu_writes_note_markdown_from_metadata_description(tmp_path):
    result = ExtractResult(
        platform="xiaohongshu",
        source="https://xhslink.com/example",
        task_id="task123",
        title="报恩伞！粉珍珠点白太真",
        author=None,
        webpage_url="https://www.xiaohongshu.com/discovery/item/example",
        audio_path=str(tmp_path / "task123" / "assets" / "audio.wav"),
        video_path=None,
        metadata={
            "title": "报恩伞！粉珍珠点白太真",
            "description": "详细记录下自己洗五金过程\n用了217石头 3k6",
        },
    )

    with patch("extractors.xiaohongshu.YtDlpExtractor.extract", return_value=result):
        extracted = Extractor().extract("https://xhslink.com/example", tmp_path)

    article = tmp_path / extracted.task_id / "article.md"
    assert article.exists()
    article_text = article.read_text(encoding="utf-8")
    assert article_text.startswith("# 报恩伞！粉珍珠点白太真")
    assert "详细记录下自己洗五金过程" in article_text
