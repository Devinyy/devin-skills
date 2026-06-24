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
XIAOHONGSHU_COOKIE_FILE=/path/to/xhs-cookies.txt
WECHAT_COOKIE_FILE=/path/to/wechat-cookies.txt
WECHAT_CHANNELS_COOKIE_FILE=/path/to/wechat-channels-cookies.txt
```

## Variable Notes

- `DOUYIN_COOKIE_FILE` is used by Douyin Playwright fallback.
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

1. Open the link in the same browser.
2. Complete verification.
3. Confirm the video page loads normally.
4. Export cookies again.
5. Re-run extraction with `DOUYIN_COOKIE_FILE=/path/to/cookies.txt`.

