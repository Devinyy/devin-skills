#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from urllib.parse import urlparse

LOCAL_EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".mp3", ".m4a", ".wav", ".flac", ".aac"}

URL_RE = re.compile(r"https?://[^\s，。；、]+")

PLATFORM_DOMAINS = [
    ("bilibili", ["bilibili.com", "b23.tv"]),
    ("douyin", ["douyin.com", "iesdouyin.com"]),
    ("xiaohongshu", ["xiaohongshu.com", "xhslink.com"]),
    ("wechat_article", ["mp.weixin.qq.com"]),
    ("wechat_channels", ["channels.weixin.qq.com"]),
]


def host_matches(host: str, domain: str) -> bool:
    return host == domain or host.endswith(f".{domain}")


def detect(value: str) -> dict:
    value = value.strip()
    match = URL_RE.search(value)
    probe = match.group(0) if match else value
    _, ext = os.path.splitext(probe.lower())
    if os.path.exists(probe) or ext in LOCAL_EXTS:
        return {"platform": "local_file", "input": probe, "confidence": 0.99}

    parsed = urlparse(probe if re.match(r"^https?://", probe) else "https://" + probe)
    host = parsed.hostname.lower() if parsed.hostname else ""
    path = parsed.path.lower()

    for platform, domains in PLATFORM_DOMAINS:
        for domain in domains:
            if host_matches(host, domain):
                return {"platform": platform, "input": probe, "confidence": 0.95}
    if host_matches(host, "weixin.qq.com") and path.startswith("/sph"):
        return {"platform": "wechat_channels", "input": probe, "confidence": 0.95}

    return {"platform": "unknown", "input": value, "confidence": 0.2}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    args = parser.parse_args()
    print(json.dumps(detect(args.input), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
