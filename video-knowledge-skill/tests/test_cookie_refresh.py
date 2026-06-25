from pathlib import Path

from scripts.cookie_refresh import filter_netscape_cookie_file


def test_filter_netscape_cookie_file_keeps_allowed_domains(tmp_path):
    source = tmp_path / "all.txt"
    target = tmp_path / "douyin.txt"
    source.write_text(
        "\n".join(
            [
                "# Netscape HTTP Cookie File",
                ".douyin.com\tTRUE\t/\tTRUE\t9999999999\tsid_guard\tabc",
                ".iesdouyin.com\tTRUE\t/\tTRUE\t9999999999\tmsToken\tdef",
                ".example.com\tTRUE\t/\tTRUE\t9999999999\tother\tghi",
            ]
        ),
        encoding="utf-8",
    )

    kept = filter_netscape_cookie_file(source, target, ["douyin.com", "iesdouyin.com"])

    text = target.read_text(encoding="utf-8")
    assert kept == 2
    assert "sid_guard" in text
    assert "msToken" in text
    assert "example.com" not in text
