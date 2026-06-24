from __future__ import annotations

from http.cookiejar import MozillaCookieJar
from typing import Iterable

from playwright.sync_api import sync_playwright


def domain_matches(host: str, domain: str) -> bool:
    normalized_host = host.lstrip(".")
    normalized_domain = domain.lstrip(".")
    return normalized_host == normalized_domain or normalized_host.endswith(f".{normalized_domain}")


def load_playwright_cookies(cookie_file: str | None, allowed_domains: Iterable[str]) -> list[dict]:
    if not cookie_file:
        return []
    jar = MozillaCookieJar(cookie_file)
    jar.load(ignore_discard=True, ignore_expires=True)
    cookies = []
    for cookie in jar:
        if not any(domain_matches(cookie.domain, domain) for domain in allowed_domains):
            continue
        if not cookie.name or not isinstance(cookie.value, str):
            continue
        cookies.append(
            {
                "name": str(cookie.name),
                "value": str(cookie.value),
                "domain": cookie.domain.lstrip("."),
                "path": cookie.path or "/",
                "expires": cookie.expires or -1,
                "httpOnly": False,
                "secure": bool(cookie.secure),
                "sameSite": "Lax",
            }
        )
    return cookies


def capture_browser_page(
    source: str,
    *,
    user_agent: str,
    locale: str = "zh-CN",
    viewport: dict | None = None,
    cookies: list[dict] | None = None,
    on_response=None,
    wait_until: str = "domcontentloaded",
    timeout_ms: int = 60_000,
    poll_count: int = 30,
    poll_ms: int = 500,
    done=None,
) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=user_agent,
            locale=locale,
            viewport=viewport or {"width": 1280, "height": 900},
        )
        if cookies:
            context.add_cookies(cookies)
        page = context.new_page()
        if on_response:
            page.on("response", on_response)
        page.goto(source, wait_until=wait_until, timeout=timeout_ms)
        for _ in range(poll_count):
            page.wait_for_timeout(poll_ms)
            if done and done():
                break
        browser.close()
