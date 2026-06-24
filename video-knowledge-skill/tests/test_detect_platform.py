from scripts.detect_platform import detect


def test_detects_bilibili_domains():
    assert detect("https://www.bilibili.com/video/BV1xx411c7mD")["platform"] == "bilibili"
    assert detect("https://b23.tv/abc123")["platform"] == "bilibili"


def test_detects_phase_two_and_wechat_domains():
    assert detect("https://www.douyin.com/video/123")["platform"] == "douyin"
    assert detect("https://v.douyin.com/example/")["platform"] == "douyin"
    assert detect("https://live.douyin.com/example")["platform"] == "douyin"
    assert detect("https://xhslink.com/a/b")["platform"] == "xiaohongshu"
    assert detect("https://mp.weixin.qq.com/s/example")["platform"] == "wechat_article"
    assert detect("https://channels.weixin.qq.com/platform/post/123")["platform"] == "wechat_channels"


def test_detects_url_inside_share_text():
    share = "点击链接看看这个作品 https://v.douyin.com/TaD2t8lWUH0/ 02/16 sRk:/"
    detected = detect(share)
    assert detected["platform"] == "douyin"
    assert detected["input"] == "https://v.douyin.com/TaD2t8lWUH0/"


def test_detects_local_file_by_existing_path(tmp_path):
    video = tmp_path / "sample.mp4"
    video.write_bytes(b"not a real video")
    assert detect(str(video))["platform"] == "local_file"
