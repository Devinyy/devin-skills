from unittest.mock import Mock, patch

from extractors.wechat_article import Extractor, parse_article, find_embedded_video_urls


def test_parse_article_extracts_title_author_and_text():
    html = """
    <html>
      <meta property="og:title" content="文章标题">
      <body>
        <h1 id="activity-name"><span>页面标题</span></h1>
        <a id="js_name">作者名</a>
        <div id="js_content"><p>第一段</p><p>第二段</p></div>
      </body>
    </html>
    """

    article = parse_article(html)

    assert article["title"] == "页面标题"
    assert article["author"] == "作者名"
    assert "第一段" in article["text"]
    assert "第二段" in article["text"]


def test_find_embedded_video_urls_ignores_ad_video_ids_without_media_url():
    html = """
    <div id="js_content"><p>正文</p></div>
    <script>
      var defaultMidAdData = {
        url: 'https://ad.weixin.qq.com/guide/196?gdt_vid=wx0clsqxat6lzly601'
      };
    </script>
    """

    assert find_embedded_video_urls(html) == []


def test_find_embedded_video_urls_finds_content_video_sources():
    html = """
    <div id="js_content">
      <video data-src="https://example.test/content.mp4"></video>
      <iframe data-src="https://mp.weixin.qq.com/mp/videoplayer?vid=wx123"></iframe>
    </div>
    """

    assert find_embedded_video_urls(html) == [
        "https://example.test/content.mp4",
        "https://mp.weixin.qq.com/mp/videoplayer?vid=wx123",
    ]


def test_wechat_article_extractor_writes_article_markdown_without_video(tmp_path):
    response = Mock()
    response.content = """
    <html>
      <body>
        <h1 id="activity-name"><span>页面标题</span></h1>
        <a id="js_name">作者名</a>
        <div id="js_content"><p>第一段</p><p>第二段</p></div>
      </body>
    </html>
    """.encode("utf-8")
    response.encoding = "utf-8"
    response.raise_for_status.return_value = None

    with patch("extractors.wechat_article.requests.get", return_value=response):
        result = Extractor().extract("https://mp.weixin.qq.com/s/example", tmp_path)

    task_dir = tmp_path / result.task_id
    assert result.platform == "wechat_article"
    assert result.title == "页面标题"
    assert result.metadata["content_type"] == "article"
    assert (task_dir / "article.md").read_text(encoding="utf-8").startswith("# 页面标题")
    assert (task_dir / "metadata.json").exists()
