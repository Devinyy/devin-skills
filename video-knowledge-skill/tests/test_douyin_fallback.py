from unittest.mock import Mock, patch

from yt_dlp.utils import DownloadError

from extractors.douyin import Extractor
from extractors.yt_dlp_extractor import YtDlpExtractor


def test_douyin_falls_back_to_browser_aweme_detail_when_yt_dlp_needs_cookies(tmp_path):
    aweme = {
        "aweme_id": "7575945613952029115",
        "desc": "如何在草台班子保持自洽。",
        "duration": 135734,
        "author": {"nickname": "狠人认知局"},
        "video": {
            "play_addr": {
                "url_list": ["https://example.test/source.mp4"],
            }
        },
    }

    with (
        patch.object(YtDlpExtractor, "extract", side_effect=DownloadError("Fresh cookies are needed")),
        patch.object(Extractor, "_fetch_aweme_detail_with_browser", return_value=aweme),
        patch("extractors.douyin.requests.get") as get,
        patch("extractors.douyin.normalize_audio", side_effect=lambda source, output: output),
    ):
        get.return_value.raise_for_status.return_value = None
        get.return_value.iter_content.return_value = [b"video-bytes"]

        result = Extractor().extract("https://v.douyin.com/TaD2t8lWUH0/", tmp_path)

    assert result.platform == "douyin"
    assert result.title == "如何在草台班子保持自洽。"
    assert result.author == "狠人认知局"
    assert result.audio_path.endswith("assets/audio.wav")
    assert (tmp_path / result.task_id / "assets" / "source.mp4").read_bytes() == b"video-bytes"


def test_douyin_finds_aweme_detail_recursively():
    payload = {
        "router": {
            "loaderData": {
                "video": {
                    "aweme_detail": {
                        "aweme_id": "123",
                        "desc": "递归详情",
                        "video": {"play_addr": {"url_list": ["https://example.test/a.mp4"]}},
                    }
                }
            }
        }
    }

    detail = Extractor()._find_aweme_detail(payload)

    assert detail["aweme_id"] == "123"
    assert detail["desc"] == "递归详情"


def test_douyin_jina_reader_url_uses_original_source_prefix(monkeypatch):
    seen = {}

    def fake_get(url, **kwargs):
        seen["url"] = url

        class Response:
            text = "Title: 抖音内容\n\n正文"

            def raise_for_status(self):
                return None

        return Response()

    monkeypatch.setattr("extractors.douyin.requests.get", fake_get)

    markdown = Extractor()._fetch_jina_markdown("https://v.douyin.com/example/")

    assert markdown.startswith("Title:")
    assert seen["url"] == "https://r.jina.ai/https://v.douyin.com/example/"
