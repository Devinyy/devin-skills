# Cookie Guide

Some platforms require browser cookies because public pages may rely on login state, verification state, or runtime signatures.

## Recommended Pattern

1. Open the target platform in a normal browser.
2. Log in if needed.
3. Pass any captcha or verification page in the browser.
4. Export cookies to a Netscape-format cookie file.
5. Save the cookie file outside version control.
6. Configure `.env` or pass environment variables when running commands.

```env
BILIBILI_COOKIE_FILE=/path/to/bilibili-cookies.txt
DOUYIN_COOKIE_FILE=/path/to/douyin-cookies.txt
DOUYIN_AUTO_REFRESH_COOKIES=1
DOUYIN_COOKIE_BROWSER=chrome
XIAOHONGSHU_COOKIE_FILE=/path/to/xhs-cookies.txt
WECHAT_COOKIE_FILE=/path/to/wechat-cookies.txt
WECHAT_CHANNELS_COOKIE_FILE=/path/to/wechat-channels-cookies.txt
```

## Variable Notes

- `DOUYIN_COOKIE_FILE` is used by Douyin Playwright fallback.
- `DOUYIN_AUTO_REFRESH_COOKIES=1` enables automatic refresh when yt-dlp reports stale Douyin cookies.
- `DOUYIN_COOKIE_BROWSER` selects the local browser profile used by yt-dlp cookie extraction, such as `chrome`, `chromium`, or `edge`.
- `WECHAT_CHANNELS_COOKIE_FILE` is supported for video号-specific cookies.
- `WECHAT_COOKIE_FILE` remains a generic WeChat fallback variable.
- Cookie files should not be committed. This repository ignores `*cookies*.txt`.

## Security

- Do not commit cookie files.
- Do not share cookie files.
- Rotate cookies if leaked.
- Prefer storing cookie files outside the skill directory.
- If a cookie file must temporarily live in this directory, keep the `*cookies*.txt` ignore rule.

## Troubleshooting

If Douyin still reports fresh cookies are needed:

1. Make sure Douyin is already logged in inside the browser selected by `DOUYIN_COOKIE_BROWSER`.
2. Run `python scripts/refresh-cookies.py douyin` to export fresh cookies to `DOUYIN_COOKIE_FILE` or `www.douyin.com_cookies.txt`.
3. Re-run extraction with `DOUYIN_COOKIE_FILE=/path/to/cookies.txt`.

During normal Douyin extraction, if yt-dlp reports that fresh cookies are needed, the extractor automatically runs the same refresh flow once and retries before falling back to Playwright/Jina page text. This does not bypass captcha, SMS, QR login, or platform verification. If the browser itself is logged out or blocked by verification, the automatic refresh cannot create a valid logged-in session.
