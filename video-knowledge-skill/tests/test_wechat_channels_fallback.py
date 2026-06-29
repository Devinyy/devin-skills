from unittest.mock import Mock, patch

import pytest
from yt_dlp.utils import DownloadError

from extractors.base import InsufficientContentError
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


def test_wechat_channels_rejects_preview_only_content(tmp_path):
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
        with pytest.raises(InsufficientContentError, match="placeholder note"):
            Extractor().extract("https://weixin.qq.com/sph/ATuxyDQm1V", tmp_path)

    assert not list(tmp_path.rglob("article.md"))
    assert not list(tmp_path.iterdir())
