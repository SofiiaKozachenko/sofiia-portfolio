#!/usr/bin/env python3
"""Generate compact, responsive WebP character images from the original lossless asset.

No character retouching or compositional changes. Keep transparent edges; produce
one high-quality 915px desktop image and one 640px phone/portrait image.
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "assets" / "sofiia-fullbody-original.webp"
asset_dir = ROOT / "dist" / "assets"

if not source.is_file() or source.stat().st_size < 100_000:
    raise SystemExit("Cannot publish: original full-body character is missing or empty")

asset_dir.mkdir(parents=True, exist_ok=True)
with Image.open(source) as portrait:
    portrait.load()
    if portrait.size != (915, 2048):
        raise SystemExit(f"Unexpected original character dimensions: {portrait.size}")
    original = portrait.convert("RGBA")
    for name, target_width in (
        ("sofiia-character-mobile.webp", 640),
        ("sofiia-character-optimized.webp", 915),
    ):
        output = asset_dir / name
        image = original if target_width == original.width else original.resize(
            (target_width, round(original.height * target_width / original.width)),
            Image.Resampling.LANCZOS,
        )
        image.save(output, "WEBP", quality=86, method=6, alpha_quality=100, exact=True)
        with Image.open(output) as check:
            check.verify()
        size = output.stat().st_size
        if not 20_000 < size < 450_000:
            raise SystemExit(f"Unexpected optimized portrait size: {name} {size} bytes")
        print(f"Optimized portrait: {name}, {size} bytes", flush=True)

# Prevent the previous heavy PNG from being carried over when restoring a
# previously successful Pages artifact.
legacy = asset_dir / "sofiia-character-clean-v31.png"
if legacy.exists():
    legacy.unlink()
