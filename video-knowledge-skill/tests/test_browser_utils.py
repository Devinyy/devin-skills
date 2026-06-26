from http.cookiejar import Cookie, MozillaCookieJar

from extractors.browser_utils import MAX_PLAYWRIGHT_EXPIRES, load_playwright_cookies


def make_cookie(name, value, domain=".douyin.com"):
    return Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain=domain,
        domain_specified=True,
        domain_initial_dot=domain.startswith("."),
        path="/",
        path_specified=True,
        secure=False,
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={},
        rfc2109=False,
    )


def test_load_playwright_cookies_filters_domains_and_invalid_values(tmp_path):
    jar_path = tmp_path / "cookies.txt"
    jar = MozillaCookieJar(str(jar_path))
    jar.set_cookie(make_cookie("sessionid", "abc", ".douyin.com"))
    jar.set_cookie(make_cookie("other", "skip", ".example.com"))
    jar.save(ignore_discard=True, ignore_expires=True)

    cookies = load_playwright_cookies(str(jar_path), ["douyin.com"])

    assert [cookie["name"] for cookie in cookies] == ["sessionid"]
    assert cookies[0]["domain"] == "douyin.com"


def test_load_playwright_cookies_clamps_large_expires(tmp_path):
    cookie_file = tmp_path / "cookies.txt"
    cookie_file.write_text(
        "\n".join(
            [
                "# Netscape HTTP Cookie File",
                ".douyin.com\tTRUE\t/\tTRUE\t13432212066256452\tsid_guard\tabc",
            ]
        ),
        encoding="utf-8",
    )

    cookies = load_playwright_cookies(str(cookie_file), ["douyin.com"])

    assert cookies[0]["expires"] == MAX_PLAYWRIGHT_EXPIRES
