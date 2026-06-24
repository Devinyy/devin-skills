from unittest.mock import Mock, patch

from yt_dlp.utils import DownloadError

from extractors.bilibili import Extractor
from extractors.yt_dlp_extractor import YtDlpExtractor


class FakeResponse:
    def __init__(self, payload=None, chunks=None):
        self.payload = payload
        self.chunks = chunks or []

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload

    def iter_content(self, chunk_size=1024 * 1024):
        yield from self.chunks


def test_bilibili_falls_back_to_public_api_when_yt_dlp_playurl_is_blocked(tmp_path):
    view_payload = {
        "code": 0,
        "data": {
            "bvid": "BV1o34y1g7WS",
            "aid": 832289817,
            "cid": 1303174115,
            "title": "给父母送礼有多难？！",
            "duration": 1478,
            "owner": {"name": "大物是也"},
            "pages": [{"cid": 1303174115, "page": 1, "part": "P1"}],
        },
    }
    play_payload = {
        "code": 0,
        "data": {
            "dash": {
                "audio": [
                    {"baseUrl": "https://example.test/audio.m4s", "bandwidth": 100},
                    {"baseUrl": "https://example.test/audio-high.m4s", "bandwidth": 200},
                ]
            }
        },
    }

    session = Mock()
    session.get.side_effect = [
        FakeResponse(view_payload),
        FakeResponse(play_payload),
        FakeResponse(chunks=[b"audio-bytes"]),
    ]

    with (
        patch.object(YtDlpExtractor, "extract", side_effect=DownloadError("HTTP Error 412")),
        patch("extractors.bilibili.requests.Session", return_value=session),
        patch("extractors.bilibili.normalize_audio", side_effect=lambda source, output: output),
    ):
        result = Extractor().extract("https://www.bilibili.com/video/BV1o34y1g7WS/", tmp_path)

    assert result.platform == "bilibili"
    assert result.title == "给父母送礼有多难？！"
    assert result.author == "大物是也"
    assert result.audio_path.endswith("assets/audio.wav")
    assert (tmp_path / result.task_id / "assets" / "source.m4s").read_bytes() == b"audio-bytes"
