#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qiniu (七牛云) icon uploader — pure stdlib, no SDK required.

Capabilities (matches the three rules):
  1. Reuse:   before uploading, `stat` the target key. If it already exists AND
              its content hash matches the local file, reuse the existing URL.
              (Same name + same content -> no re-upload.)
  2. Classify: decide whether an icon is a `common/` asset or a page-specific
              asset (`<page>/...`) from its file name, using keyword/prefix rules
              from the config. Upload into the matching root-level folder.
  3. Output:  print the final CDN URL so the caller can replace it in code.

Subcommands:
  classify NAME [--page PAGE]            -> print {folder, key} (no network)
  upload   FILE [--page PAGE] [--name N] -> classify + reuse-check + upload, print {url, key, reused, action}

Config: <skill-root>/config.local.json  (see config.example.json). Override with
--config PATH or env QINIU_CONFIG. Never commit config.local.json (gitignored).
"""
import argparse
import base64
import hashlib
import hmac
import json
import mimetypes
import os
import sys
import time
import urllib.request
import urllib.error
import uuid

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOCK_SIZE = 1 << 22  # 4 MiB

DEFAULT_COMMON_KEYWORDS = [
    "common", "back", "arrow", "close", "delete", "add", "minus", "plus",
    "check", "checked", "uncheck", "selected", "search", "clear", "location",
    "share", "more", "star", "heart", "like", "scan", "edit", "setting",
    "loading", "empty", "success", "fail", "warning", "tip", "dropdown",
    "up", "down", "left", "right", "logo", "default", "avatar", "placeholder",
]
DEFAULT_COMMON_PREFIXES = ["common_", "common-", "ic_common_", "icon_common_", "ic_", "icon_"]


# ----------------------------- config -----------------------------
def load_config(path=None):
    path = path or os.environ.get("QINIU_CONFIG") or os.path.join(SKILL_ROOT, "config.local.json")
    if not os.path.exists(path):
        die(f"config not found: {path}\n"
            f"  copy config.example.json -> config.local.json and fill in your keys.")
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    for k in ("access_key", "secret_key", "bucket", "domain"):
        if not cfg.get(k):
            die(f"config missing required field: {k}")
    cfg.setdefault("up_host", "https://up-z0.qiniup.com")
    cfg.setdefault("rs_host", "https://rs.qiniuapi.com")
    cfg.setdefault("base_prefix", "")  # e.g. "images" -> keys become images/<folder>/<name>
    cfg.setdefault("common_folder", "common")
    cfg.setdefault("page_subfolder", True)  # False -> page-specific files go flat under base_prefix (no <page>/)
    cfg.setdefault("common_keywords", DEFAULT_COMMON_KEYWORDS)
    cfg.setdefault("common_prefixes", DEFAULT_COMMON_PREFIXES)
    # normalize domain -> scheme + host, no trailing slash
    dom = cfg["domain"].strip().rstrip("/")
    if not dom.startswith("http://") and not dom.startswith("https://"):
        dom = ("https://" if cfg.get("use_https", True) else "http://") + dom
    cfg["domain"] = dom
    return cfg


# ----------------------------- helpers -----------------------------
def die(msg, code=1):
    print(f"[qiniu] ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def info(msg):
    print(f"[qiniu] {msg}", file=sys.stderr)


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii")


def normalize_name(name: str) -> str:
    """basename, lower-cased extension; keep stem as-is."""
    base = os.path.basename(name)
    stem, ext = os.path.splitext(base)
    return stem + ext.lower()


def classify(name: str, cfg: dict, page: str = None):
    """Return (folder, key). page-specific unless name looks common."""
    fname = normalize_name(name)
    stem = os.path.splitext(fname)[0].lower()
    is_common = False
    for p in cfg["common_prefixes"]:
        if stem.startswith(p):
            is_common = True
            break
    if not is_common:
        tokens = stem.replace("-", "_").split("_")
        kws = set(cfg["common_keywords"])
        if any(t in kws for t in tokens):
            is_common = True
    prefix = cfg.get("base_prefix", "").strip("/")
    if is_common:
        folder = cfg["common_folder"].strip("/")
    elif cfg.get("page_subfolder", True):
        if not page:
            die(f"cannot classify '{fname}' as common, and no --page given.\n"
                f"  pass --page <name> for a page-specific icon, or rename to a common keyword/prefix.")
        folder = page.strip("/")
    else:
        folder = ""  # flat: page-specific files land directly under base_prefix
    key = "/".join(p for p in (prefix, folder, fname) if p)
    return (folder or prefix), key


# ----------------------------- qiniu etag -----------------------------
def qiniu_etag(filepath: str) -> str:
    size = os.path.getsize(filepath)
    with open(filepath, "rb") as f:
        if size <= BLOCK_SIZE:
            digest = bytes([0x16]) + hashlib.sha1(f.read()).digest()
        else:
            block_sha1s = b""
            while True:
                chunk = f.read(BLOCK_SIZE)
                if not chunk:
                    break
                block_sha1s += hashlib.sha1(chunk).digest()
            digest = bytes([0x96]) + hashlib.sha1(block_sha1s).digest()
    return b64u(digest)


# ----------------------------- tokens -----------------------------
def upload_token(cfg, key, expires=3600):
    deadline = int(time.time()) + expires
    policy = {"scope": f"{cfg['bucket']}:{key}", "deadline": deadline}
    encoded = b64u(json.dumps(policy, separators=(",", ":")).encode())
    sign = hmac.new(cfg["secret_key"].encode(), encoded.encode(), hashlib.sha1).digest()
    return f"{cfg['access_key']}:{b64u(sign)}:{encoded}"


def access_token(cfg, path, query="", body=b""):
    data = path
    if query:
        data += "?" + query
    data += "\n"
    raw = data.encode() + (body if isinstance(body, bytes) else body.encode())
    sign = hmac.new(cfg["secret_key"].encode(), raw, hashlib.sha1).digest()
    return f"QBox {cfg['access_key']}:{b64u(sign)}"


# ----------------------------- API calls -----------------------------
def stat(cfg, key):
    """Return remote file info dict, or None if not found."""
    entry = b64u(f"{cfg['bucket']}:{key}".encode())
    path = f"/stat/{entry}"
    url = cfg["rs_host"].rstrip("/") + path
    req = urllib.request.Request(url, headers={"Authorization": access_token(cfg, path)})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code in (612, 404):  # no such file
            return None
        body = e.read().decode(errors="replace")
        die(f"stat failed ({e.code}): {body}")
    except urllib.error.URLError as e:
        die(f"stat network error: {e}")


def form_upload(cfg, key, filepath):
    token = upload_token(cfg, key)
    boundary = "----QiniuFormBoundary" + uuid.uuid4().hex
    with open(filepath, "rb") as f:
        content = f.read()
    ctype = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
    fname = normalize_name(filepath)

    def part(name, value):
        return (f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n'
                f'{value}\r\n').encode()

    body = b""
    body += part("token", token)
    body += part("key", key)
    body += (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; '
             f'filename="{fname}"\r\nContent-Type: {ctype}\r\n\r\n').encode()
    body += content + b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    url = cfg["up_host"].rstrip("/")
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        die(f"upload failed ({e.code}): {body}")
    except urllib.error.URLError as e:
        die(f"upload network error: {e}")


# ----------------------------- commands -----------------------------
def cmd_classify(args):
    cfg = load_config(args.config)
    folder, key = classify(args.name, cfg, args.page)
    out = {"folder": folder, "key": key, "url": f"{cfg['domain']}/{key}"}
    print(json.dumps(out, ensure_ascii=False))


def cmd_upload(args):
    cfg = load_config(args.config)
    if not os.path.isfile(args.file):
        die(f"file not found: {args.file}")
    name = args.name or args.file
    folder, key = classify(name, cfg, args.page)
    url = f"{cfg['domain']}/{key}"
    local_etag = qiniu_etag(args.file)

    action = "uploaded"
    reused = False
    if not args.force:
        remote = stat(cfg, key)
        if remote is not None:
            if args.reuse_by_name or remote.get("hash") == local_etag:
                reused = True
                action = "reused" if remote.get("hash") == local_etag else "reused-by-name"
                info(f"reuse existing {key} (hash {'match' if remote.get('hash') == local_etag else 'IGNORED by --reuse-by-name'})")
            else:
                action = "overwritten"
                info(f"{key} exists but content changed -> re-uploading")
    if not reused:
        res = form_upload(cfg, key, args.file)
        if res.get("key") != key:
            info(f"warning: returned key {res.get('key')} != {key}")

    out = {"url": url, "key": key, "folder": folder,
           "reused": reused, "action": action, "etag": local_etag}
    print(json.dumps(out, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description="Qiniu icon uploader")
    p.add_argument("--config", help="path to config.local.json")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("classify", help="print folder/key without network")
    pc.add_argument("name")
    pc.add_argument("--page", help="page name for page-specific icons")
    pc.set_defaults(func=cmd_classify)

    pu = sub.add_parser("upload", help="classify, reuse-check, upload")
    pu.add_argument("file")
    pu.add_argument("--page", help="page name for page-specific icons")
    pu.add_argument("--name", help="override remote file name (default: local basename)")
    pu.add_argument("--force", action="store_true", help="always upload, skip reuse check")
    pu.add_argument("--reuse-by-name", action="store_true",
                    help="reuse on name match even if content differs")
    pu.set_defaults(func=cmd_upload)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
