from unittest.mock import Mock, patch

from scripts import summarize


def test_summarize_uses_article_markdown_when_transcript_is_absent(tmp_path):
    (tmp_path / "article.md").write_text("# 文章标题\n\n## 正文\n\n文章内容", encoding="utf-8")
    (tmp_path / "metadata.json").write_text("{}", encoding="utf-8")

    client = Mock()
    client.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="# 标题\n\n## 一句话总结\n文章总结"))
    ]

    with (
        patch("scripts.summarize.load_dotenv"),
        patch("scripts.summarize.OpenAI", return_value=client),
    ):
        summarize.summarize(str(tmp_path))

    messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert "文章内容" in messages[1]["content"]
    assert "内容：" in messages[1]["content"]


def test_summarize_includes_article_markdown_alongside_transcript(tmp_path):
    (tmp_path / "transcript.md").write_text("低质量字幕", encoding="utf-8")
    (tmp_path / "article.md").write_text("# 笔记标题\n\n## 正文\n\n笔记正文", encoding="utf-8")
    (tmp_path / "metadata.json").write_text("{}", encoding="utf-8")

    client = Mock()
    client.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="# 标题\n\n## 一句话总结\n合并总结"))
    ]

    with (
        patch("scripts.summarize.load_dotenv"),
        patch("scripts.summarize.OpenAI", return_value=client),
    ):
        summarize.summarize(str(tmp_path))

    messages = client.chat.completions.create.call_args.kwargs["messages"]
    content = messages[1]["content"]
    assert "字幕：" in content
    assert "低质量字幕" in content
    assert "文章或笔记内容：" in content
    assert "笔记正文" in content


def test_summarize_uses_requested_summary_style(tmp_path):
    (tmp_path / "article.md").write_text("文章内容", encoding="utf-8")
    (tmp_path / "metadata.json").write_text("{}", encoding="utf-8")

    client = Mock()
    client.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="# 笔记"))
    ]

    with (
        patch("scripts.summarize.load_dotenv"),
        patch("scripts.summarize.OpenAI", return_value=client),
    ):
        summarize.summarize(str(tmp_path), summary_style="note")

    messages = client.chat.completions.create.call_args.kwargs["messages"]
    assert "## B. 可收藏笔记" in messages[0]["content"]
    assert "## A. 忠实摘要" not in messages[0]["content"]


def test_summarize_writes_title_named_markdown_and_metadata(tmp_path):
    (tmp_path / "article.md").write_text("文章内容", encoding="utf-8")
    (tmp_path / "metadata.json").write_text('{"source":"https://example.com/article"}', encoding="utf-8")

    client = Mock()
    client.chat.completions.create.return_value.choices = [
        Mock(message=Mock(content="# 字节跳动技术副总裁洪定坤：AI Coding 的实践与探索\n\n内容"))
    ]

    with (
        patch("scripts.summarize.load_dotenv"),
        patch("scripts.summarize.OpenAI", return_value=client),
    ):
        summarize.summarize(str(tmp_path))

    named = tmp_path / "字节跳动技术副总裁洪定坤：AI Coding 的实践与探索.md"
    assert (tmp_path / "summary.md").exists()
    assert named.exists()
    assert named.read_text(encoding="utf-8").startswith("# 字节跳动技术副总裁洪定坤")
    assert "## 原链接\n\nhttps://example.com/article" in (tmp_path / "summary.md").read_text(encoding="utf-8")
    assert "## 原链接\n\nhttps://example.com/article" in named.read_text(encoding="utf-8")

    metadata = __import__("json").loads((tmp_path / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["summary_path"] == str(tmp_path / "summary.md")
    assert metadata["summary_named_path"] == str(named)


def test_source_link_replaces_existing_source_block():
    markdown = "# 标题\n\n内容\n\n## 原链接\n\nhttps://old.example"

    result = summarize.with_source_link(markdown, "https://new.example")

    assert result.count("## 原链接") == 1
    assert "https://new.example" in result
    assert "https://old.example" not in result
