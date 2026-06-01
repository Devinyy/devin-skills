---
name: qiniu-icon-upload
version: 1.0.1
description: Use when icons (切图) need to become hosted Qiniu (七牛云) CDN URLs — uploads local PNG/SVG icons (or layers exported from a Figma design) to Qiniu with same-name reuse and common/page-specific classification, then replaces the local /static/icon paths in code with the CDN URLs. Triggers on requests like "上传这些图标到七牛云并替换链接", "把切图传到 CDN", or implementing a Figma design whose layers carry the slice/export marker (icon_xxx).
---

# Qiniu Icon Upload (七牛云切图上传)

Turn Figma 切图 icons into hosted Qiniu URLs and wire them into the code, in one pass.

## When to use

- You have local PNG/SVG icons (切图) that should live on the Qiniu CDN instead of
  `/static/icon/` — any "上传这些图标到七牛云" / "把切图传到 CDN 并替换链接" request.
- Implementing a Figma design where layers carry the slice/export marker
  (`icon_xxx`) — these are image 切图 assets, NOT things to rebuild in CSS.
- Running in a shell / CI step that needs to push icons to Qiniu and get back CDN
  URLs (use the `scripts/*.py` directly; the uploader is pure stdlib).

Do **not** use for photographic content review or for icons that are actually
pure CSS shapes.

## Prerequisites (one-time)

1. `cp config.example.json config.local.json` in this skill's root.
2. Fill in `access_key`, `secret_key`, `bucket`, `domain`. `config.local.json` is
   gitignored — never commit it, never paste the keys into chat.
3. Python 3 (stdlib only — no SDK needed). Pillow is used by `prepare_png.py`.

## Rules this skill enforces

1. **Reuse** — before uploading, the script `stat`s the target key. If the file
   already exists with the **same content hash**, it reuses the existing URL
   (no re-upload). Same name + changed content → it overwrites and reports
   `action: "overwritten"`.
2. **Classify** — common vs page-specific is decided from the file name:
   - name starts with a `common_*` prefix, OR contains a common keyword
     (`back`, `arrow`, `close`, `location`, …) → `common/` folder.
   - otherwise → `<page>/` folder (you must pass `--page <name>`).
   - Lists live in `config.local.json` (`common_prefixes`, `common_keywords`) —
     editable. See [references/classification.md](references/classification.md).
3. **Replace** — the script prints the final CDN URL; you replace the local
   path / placeholder in the code with that URL.

Qiniu layout: `<base_prefix>/common/<name>.png`, `<base_prefix>/<page>/<name>.png`.
This project sets `base_prefix: "images"` (matching its `generateGlobalKey` →
`images/...` convention) and `domain: https://static.dachuguanjia.cn`, so a common
icon lands at `https://static.dachuguanjia.cn/images/common/back.png`.
Set `base_prefix: ""` for root-level folders, or `page_subfolder: false` to put
page-specific files flat under `base_prefix` (no `<page>/`).

## Workflow

### 1. Export transparent PNG from Figma

For each layer carrying the export/slice marker (`icon_*`):

- **Preferred:** ask Figma to export the node directly as **PNG** (it is already
  transparent — no rasterization). Save to a scratch dir, e.g. `./tmp-icons/`.
- Do **NOT** use `get_screenshot` for assets — it bakes the background/opacity.
  Use the asset export URL from `get_design_context`.
- If you only have an SVG, rasterize it:
  ```bash
  python3 scripts/prepare_png.py tmp-icons/back.svg tmp-icons/back.png --scale 3
  ```
  `prepare_png.py` also works on PNG input: it trims transparent borders,
  verifies the **alpha channel exists**, and warns if the image is fully opaque
  (a sign of a baked-in background — re-export it).

Name each file in the project's convention (snake_case, e.g. `goods_arrows_left.png`).
A good name is what drives correct classification — name common icons with a
common keyword/prefix.

### 2. Upload (reuse + classify happen here)

Page-specific icon:
```bash
python3 scripts/qiniu_upload.py upload tmp-icons/banner_top.png --page home
```
Common icon (classified automatically by name):
```bash
python3 scripts/qiniu_upload.py upload tmp-icons/back.png
```
Output (stdout, JSON — parse this):
```json
{"url":"https://static.dachuguanjia.cn/images/common/back.png","key":"images/common/back.png","folder":"common","reused":true,"action":"reused","etag":"Fic..."}
```
Dry-run classification only (no network):
```bash
python3 scripts/qiniu_upload.py classify back.png
python3 scripts/qiniu_upload.py classify banner_top.png --page home
```
Flags: `--name` override remote name · `--force` always upload ·
`--reuse-by-name` reuse on name match even if content differs · `--config PATH`.

### 3. Replace the URL in code

Take `url` from the JSON and replace the local reference. In this uni-app/Vue3
project icons appear as:
```html
<image src="/static/icon/back.png" />        <!-- before -->
<image src="https://static.dachuguanjia.cn/images/common/back.png" />   <!-- after -->
<up-icon name="/static/icon/cart_good.png" /> <!-- up-icon `name` also takes a URL -->
```
Replace every occurrence of the old path. Verify the file still builds.

### Batch tip

When processing many icons, loop: export → `upload` → collect each `url` →
do the code replacements at the end. Always read the `reused`/`action` field so
you can tell the user which were freshly uploaded vs reused.

## Files

- `scripts/qiniu_upload.py` — upload/classify/reuse (pure stdlib).
- `scripts/prepare_png.py` — transparent-PNG validation + optional SVG rasterize.
- `config.example.json` — copy to `config.local.json`.
- `references/classification.md` — how common vs page is decided.
