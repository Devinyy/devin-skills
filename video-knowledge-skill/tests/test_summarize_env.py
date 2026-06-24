from unittest.mock import Mock, patch

from scripts import summarize


def test_summarize_loads_dotenv_before_creating_client(tmp_path):
    (tmp_path / "transcript.md").write_text("测试字幕", encoding="utf-8")
    (tmp_path / "metadata.json").write_text("{}", encoding="utf-8")

    client = Mock()
    client.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="# 标题\n\n## 一句话总结\n测试"))
    ]

    with (
        patch("scripts.summarize.load_dotenv") as load_dotenv,
        patch("scripts.summarize.OpenAI", return_value=client),
    ):
        summarize.summarize(str(tmp_path))

    load_dotenv.assert_called_once()
