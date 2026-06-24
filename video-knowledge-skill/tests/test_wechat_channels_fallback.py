from unittest.mock import Mock, patch

from yt_dlp.utils import DownloadError

from extractors.wechat_channels import Extractor
from extractors.yt_dlp_extractor import YtDlpExtractor


def test_wechat_channels_falls_back_to_browser_feed_info(tmp_path):
    feed = {
        "data": {
            "authorInfo": {"nickname": "脱口秀和Ta的朋友们"},
            "feedInfo": {
                "description": "要知道选择讲脱口秀对一个山东人很难。",
                "createtime": "2024年9月17日",
            },
        }
    }

    with (
        patch.object(YtDlpExtractor, "extract", side_effect=DownloadError("Unsupported URL")),
        patch.object(
            Extractor,
            "_fetch_feed_info_and_media_url_with_browser",
            return_value=(feed, "https://finder.video.qq.com/source.mp4"),
        ),
        patch("extractors.wechat_channels.requests.get") as get,
        patch("extractors.wechat_channels.normalize_audio", side_effect=lambda source, output: output),
    ):
        get.return_value.raise_for_status.return_value = None
        get.return_value.iter_content.return_value = [b"video-bytes"]

        result = Extractor().extract("https://weixin.qq.com/sph/ATuxyDQm1V", tmp_path)

    assert result.platform == "wechat_channels"
    assert result.title == "要知道选择讲脱口秀对一个山东人很难。"
    assert result.author == "脱口秀和Ta的朋友们"
    assert result.audio_path.endswith("assets/audio.wav")
    assert (tmp_path / result.task_id / "assets" / "source.mp4").read_bytes() == b"video-bytes"


def test_wechat_channels_writes_preview_article_when_video_url_is_unavailable(tmp_path):
    feed = {
        "data": {
            "authorInfo": {"nickname": "脱口秀和Ta的朋友们"},
            "feedInfo": {
                "description": "要知道选择讲脱口秀对一个山东人很难。",
                "createtime": 1726560177,
            },
        }
    }

    with (
        patch.object(YtDlpExtractor, "extract", side_effect=DownloadError("Unsupported URL")),
        patch.object(
            Extractor,
            "_fetch_feed_info_and_media_url_with_browser",
            return_value=(feed, None),
        ),
    ):
        result = Extractor().extract("https://weixin.qq.com/sph/ATuxyDQm1V", tmp_path)

    assert result.audio_path is None
    assert result.metadata["content_type"] == "preview"
    assert result.metadata["availability"] == "preview_only"
    assert result.metadata["media_status"] == "not_available"
    assert "未公开" in result.metadata["media_reason"]
    article = tmp_path / result.task_id / "article.md"
    assert article.exists()
    assert "要知道选择讲脱口秀对一个山东人很难。" in article.read_text(encoding="utf-8")
