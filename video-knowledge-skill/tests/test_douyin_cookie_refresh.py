from pathlib import Path

from yt_dlp.utils import DownloadError

from extractors.douyin import Extractor
from extractors.base import ExtractResult


def test_douyin_refreshes_cookies_on_fresh_cookie_error(tmp_path, monkeypatch):
    extractor = Extractor()
    calls = {"super": 0, "refresh": 0}

    def fake_super_extract(self, source, output_dir):
        calls["super"] += 1
        if calls["super"] == 1:
            raise DownloadError("Fresh cookies are needed")
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

    def fake_refresh(platform, output=None, cwd=None):
        calls["refresh"] += 1
        path = tmp_path / "cookies.txt"
        path.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
        return path

    monkeypatch.setattr("extractors.yt_dlp_extractor.YtDlpExtractor.extract", fake_super_extract)
    monkeypatch.setattr("extractors.douyin.refresh_cookies", fake_refresh)

    result = extractor.extract("https://v.douyin.com/example/", tmp_path)

    assert result.task_id == "task123"
    assert calls == {"super": 2, "refresh": 1}
    assert extractor.cookie_file == str(tmp_path / "cookies.txt")


def test_douyin_cookie_refresh_can_be_disabled(monkeypatch):
    monkeypatch.setenv("DOUYIN_AUTO_REFRESH_COOKIES", "0")

    assert Extractor()._should_refresh_cookies(DownloadError("Fresh cookies are needed")) is False
