# Common vs Page-specific classification

The uploader decides an icon's folder purely from its **file name** (basename,
extension lower-cased). Logic (`classify()` in `qiniu_upload.py`):

1. **Prefix match** — if the name's stem starts with any `common_prefixes`
   entry (default: `common_`, `common-`, `ic_common_`, `icon_common_`) →
   `common/`.
2. **Keyword match** — else, split the stem on `_` and `-`; if any token is in
   `common_keywords` → `common/`.
3. **Otherwise** — page-specific. You must pass `--page <name>`; the file goes to
   `<page>/`. If no `--page` is given, the script errors (so nothing lands in the
   wrong place silently).

## Examples

| file name             | --page | result key              |
|-----------------------|--------|-------------------------|
| `back.png`            | —      | `common/back.png`       |
| `common_share.png`    | —      | `common/common_share.png` |
| `location.png`        | home   | `common/location.png` (keyword wins) |
| `banner_top.png`      | home   | `home/banner_top.png`   |
| `goods_arrows_left.png` | detail | `detail/goods_arrows_left.png` |
| `cart_empty.png`      | cart   | `common/cart_empty.png` (`empty` keyword) |

## Tuning

Edit `common_prefixes` / `common_keywords` in `config.local.json`. Keep keywords
lower-case and as single tokens (matched against `_`/`-` split parts), so
`cart_back` matches `back` but `feedback` would NOT match `back` (it is one token).

If a name is genuinely ambiguous (e.g. a page icon that happens to contain a
common word), either rename it or pass `--page` and remove the offending keyword —
but prefer renaming, since the name is the single source of truth.
