from extractors.generic_article import parse_article, render_article_markdown
from scripts.detect_platform import detect


def test_detect_generic_article_for_unknown_http_url():
    result = detect("https://www.cnblogs.com/CodeBlogMan/p/18278962")

    assert result["platform"] == "generic_article"
    assert result["input"] == "https://www.cnblogs.com/CodeBlogMan/p/18278962"


def test_parse_cnblogs_article_body():
    html = """
    <html>
      <head>
        <title>文章标题 - 博客园</title>
        <meta name="author" content="CodeBlogMan" />
      </head>
      <body>
        <nav>导航</nav>
        <div id="cnblogs_post_body">
          <p>第一段内容</p>
          <p>第二段内容</p>
        </div>
        <script>ignored()</script>
      </body>
    </html>
    """

    article = parse_article(html, "https://example.test/post")
    markdown = render_article_markdown(article)

    assert article["title"] == "文章标题"
    assert article["author"] == "CodeBlogMan"
    assert "第一段内容" in article["text"]
    assert "第二段内容" in article["text"]
    assert "导航" not in article["text"]
    assert markdown.startswith("# 文章标题")
