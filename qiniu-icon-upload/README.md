# qiniu-icon-upload

> English | [简体中文](./README.zh-CN.md)

A command-line tool (and Claude Code skill) that turns Figma 切图 icons into hosted
Qiniu (七牛云) CDN URLs and wires them into the codebase — export transparent PNG →
upload (with reuse + classification) → replace the URL in code.

It works two ways:

- **As a plain CLI** — run the `scripts/*.py` directly from any shell or CI pipeline.
  The uploader is pure Python stdlib (no Qiniu SDK), so it drops into any environment.
- **As a Claude Code skill** — drop the folder into your skills directory and let the
  agent run the full Figma→upload→replace workflow. See `SKILL.md`.

## Setup

```bash
cp config.example.json config.local.json
# edit config.local.json: access_key, secret_key, bucket, domain
```

`config.local.json` holds your secret keys and is **gitignored** — never commit it.

Requirements: Python 3 (uploader is pure stdlib, no Qiniu SDK). `prepare_png.py`
needs Pillow; SVG rasterization optionally uses `cairosvg` or `rsvg-convert`.

## Quick use

```bash
# classify only (no network)
python3 scripts/qiniu_upload.py classify back.png
python3 scripts/qiniu_upload.py classify banner_top.png --page home

# upload (reuse if same name+content already on Qiniu)
python3 scripts/qiniu_upload.py upload tmp-icons/back.png            # -> common/back.png
python3 scripts/qiniu_upload.py upload tmp-icons/banner_top.png --page home

# prepare a transparent PNG (validate alpha / trim / rasterize SVG)
python3 scripts/prepare_png.py in.svg out.png --scale 3
```

Each `upload`/`classify` prints one JSON line on stdout with the final `url`, so
you can pipe it into scripts, CI steps, or other tools.

## How it works

| Rule | Behaviour |
|------|-----------|
| Reuse | `stat` the key first; same name + same content hash → reuse URL (no upload). Changed content → overwrite. |
| Classify | `common/` if the name matches a common prefix/keyword, else `<page>/` (requires `--page`). Lists in config. |
| Replace | Prints the CDN URL; you (or the agent) replace the local `/static/icon/...` path in code. |

See `SKILL.md` for the full Figma→upload→replace workflow (Claude Code mode) and
`references/classification.md` for the naming rules.
