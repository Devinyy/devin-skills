#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare a transparent PNG for upload.

- Input PNG  : verify it has an alpha channel (transparent). Optionally trim
               whitespace / re-save optimized.
- Input SVG  : rasterize to transparent PNG IF a rasterizer is available
               (cairosvg, else `rsvg-convert`). Otherwise fail with guidance.

Usage:
  python3 prepare_png.py INPUT.{png,svg} OUTPUT.png [--scale 3] [--no-trim]

Exit 0 on success; prints {"ok": true, "path": ..., "size": [w,h], "has_alpha": true}.
"""
import json
import os
import subprocess
import sys
import argparse


def die(msg, code=1):
    print(f"[prepare_png] ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def rasterize_svg(src, dst, scale):
    # 1) cairosvg (python)
    try:
        import cairosvg  # noqa
        cairosvg.svg2png(url=src, write_to=dst, scale=scale)
        return
    except ImportError:
        pass
    # 2) rsvg-convert (CLI)
    from shutil import which
    if which("rsvg-convert"):
        subprocess.run(["rsvg-convert", "-z", str(scale), "-o", dst, src], check=True)
        return
    die("no SVG rasterizer found. Either export the icon from Figma as PNG "
        "directly (preferred — transparent, no rasterization needed), or "
        "`pip install cairosvg`, or install librsvg (`brew install librsvg`).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--scale", type=float, default=1.0, help="SVG rasterize scale (e.g. 3 for @3x)")
    ap.add_argument("--no-trim", action="store_true", help="do not trim transparent borders")
    args = ap.parse_args()

    if not os.path.isfile(args.input):
        die(f"input not found: {args.input}")

    ext = os.path.splitext(args.input)[1].lower()
    tmp = args.output
    if ext == ".svg":
        rasterize_svg(args.input, tmp, args.scale)
        src = tmp
    else:
        src = args.input

    try:
        from PIL import Image
    except ImportError:
        die("Pillow not installed: pip install Pillow")

    img = Image.open(src).convert("RGBA")
    # Check transparency on the ORIGINAL (before trim): a real cutout has some
    # transparent pixels around/within the shape; a baked screenshot is a fully
    # opaque rectangle. Trimming would crop away the transparent border and make
    # every tightly-cropped icon look opaque, so measure first.
    has_alpha = img.getchannel("A").getextrema()[0] < 255

    if not args.no_trim:
        bbox = img.getbbox()  # bbox of non-zero (non-transparent) region
        if bbox:
            img = img.crop(bbox)

    img.save(args.output, "PNG", optimize=True)

    print(json.dumps({
        "ok": True,
        "path": args.output,
        "size": list(img.size),
        "has_alpha": bool(has_alpha),
    }, ensure_ascii=False))
    if not has_alpha:
        print("[prepare_png] WARNING: image has no transparent pixels — "
              "verify this is a real cutout, not a screenshot with baked background.",
              file=sys.stderr)


if __name__ == "__main__":
    main()
