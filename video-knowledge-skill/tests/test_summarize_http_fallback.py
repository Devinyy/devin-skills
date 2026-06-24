from unittest.mock import Mock, patch
import json

from openai import PermissionDeniedError

from scripts import summarize


class FakeResponse:
    content = json.dumps(
        {"choices": [{"message": {"content": "# 标题\n\n## 一句话总结\nfallback ok"}}]},
        ensure_ascii=False,
    ).encode("utf-8")

    def raise_for_status(self):
        return None


def test_summarize_falls_back_to_requests_when_openai_sdk_is_blocked(tmp_path, monkeypatch):
    (tmp_path / "transcript.md").write_text("测试字幕", encoding="utf-8")
    (tmp_path / "metadata.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")

    blocked = PermissionDeniedError(
        "blocked",
        response=Mock(status_code=403, request=Mock()),
        body={"error": {"message": "blocked"}},
    )
    client = Mock()
    client.chat.completions.create.side_effect = blocked

    with (
        patch("scripts.summarize.load_dotenv"),
        patch("scripts.summarize.OpenAI", return_value=client),
        patch("scripts.summarize.requests.post", return_value=FakeResponse()) as post,
    ):
        result = summarize.summarize(str(tmp_path))

    assert "fallback ok" in result
    assert (tmp_path / "summary.md").read_text(encoding="utf-8") == result
    post.assert_called_once()
