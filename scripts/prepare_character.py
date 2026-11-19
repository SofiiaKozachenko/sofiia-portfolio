#!/usr/bin/env python3
"""Restore the user's clean uploaded portrait as PNG for reliable mobile display.

The tracked lossless WebP contains exactly the pixels of the uploaded clean PNG.
GitHub Pages publishes the resulting PNG, leaving all source files unchanged.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "assets" / "sofiia-fullbody-original.webp"
destination = ROOT / "dist" / "assets" / "sofiia-character-clean-v31.png"

if not source.is_file() or source.stat().st_size < 100_000:
    raise SystemExit("Cannot publish: full-body character source is missing or empty")
destination.parent.mkdir(parents=True, exist_ok=True)
with Image.open(source) as portrait:
    portrait.load()
    if portrait.size != (915, 2048):
        raise SystemExit(f"Unexpected character dimensions: {portrait.size}")
    portrait.convert("RGBA").save(destination, "PNG", optimize=True)
with Image.open(destination) as check:
    check.verify()
if destination.stat().st_size < 500_000:
    raise SystemExit("Cannot publish: generated PNG is suspiciously small")
print(f"Published clean full-body PNG: {destination.stat().st_size} bytes", flush=True)
