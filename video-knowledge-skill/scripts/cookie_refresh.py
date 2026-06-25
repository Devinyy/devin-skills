from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


NETSCAPE_HEADER = "# Netscape HTTP Cookie File\n"

PLATFORM_CONFIG = {
    "douyin": {
        "env": "DOUYIN_COOKIE_FILE",
        "default": "www.douyin.com_cookies.txt",
        "probe_url": "https://www.douyin.com/",
        "domains": ["douyin.com", "iesdouyin.com"],
    },
}


def domain_matches(host: str, domain: str) -> bool:
    normalized_host = host.lstrip(".")
    normalized_domain = domain.lstrip(".")
    return normalized_host == normalized_domain or normalized_host.endswith(f".{normalized_domain}")


def default_cookie_path(platform: str, base_dir: Path | None = None) -> Path:
    config = PLATFORM_CONFIG[platform]
    env_value = os.getenv(config["env"])
    if env_value:
        return Path(env_value).expanduser()
    return (base_dir or Path.cwd()) / config["default"]


def filter_netscape_cookie_file(source: Path, target: Path, allowed_domains: list[str]) -> int:
    kept = []
    for line in source.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 7:
            continue
        domain = parts[0]
        if any(domain_matches(domain, allowed) for allowed in allowed_domains):
            kept.append(line)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        NETSCAPE_HEADER + "# Generated automatically from local browser cookies.\n\n" + "\n".join(kept) + ("\n" if kept else ""),
        encoding="utf-8",
    )
    return len(kept)


def refresh_cookies(platform: str, output: Path | None = None, browser: str | None = None, cwd: Path | None = None) -> Path:
    if platform not in PLATFORM_CONFIG:
        raise ValueError(f"Unsupported cookie refresh platform: {platform}")

    config = PLATFORM_CONFIG[platform]
    browser_name = browser or os.getenv(f"{platform.upper()}_COOKIE_BROWSER") or "chrome"
    target = output or default_cookie_path(platform, base_dir=cwd or Path.cwd())

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as fh:
        temp_path = Path(fh.name)
        fh.write(NETSCAPE_HEADER)

    try:
        command = [
            sys.executable,
            "-m",
            "yt_dlp",
            "--cookies-from-browser",
            browser_name,
            "--cookies",
            str(temp_path),
            "--skip-download",
            "--simulate",
            config["probe_url"],
        ]
        result = subprocess.run(command, cwd=str(cwd or Path.cwd()), capture_output=True, text=True, check=False)
        combined_output = f"{result.stdout}\n{result.stderr}"
        if "Extracted" not in combined_output:
            raise RuntimeError(combined_output.strip() or "yt-dlp did not report extracted browser cookies")
        kept = filter_netscape_cookie_file(temp_path, target, config["domains"])
        if kept <= 0:
            raise RuntimeError(f"No {platform} cookies found in browser {browser_name}")
        return target
    finally:
        try:
            temp_path.unlink()
        except OSError:
            pass
