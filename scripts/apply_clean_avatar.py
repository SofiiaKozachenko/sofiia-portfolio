#!/usr/bin/env python3
"""Rebuild the exact user-supplied shadow-free portrait from the original asset.

The full images are identical outside a 56x250 rectangle. This lossless
pixel-level delta ensures all original details and transparent pixels stay intact.
"""
from pathlib import Path
from PIL import Image
import base64, hashlib, io, zlib

PATH = Path(__file__).resolve().parents[1] / "assets" / "sofiia-fullbody-original.webp"
OLD_SHA = "41c91032ecf706a5e4b57862801d46ad76fdf9e0cab76a05eb1c809ae47280cd"
NEW_SHA = "f8f53127245c7affd91d1a3a131a10bf7ea1c1a9aa766d62122fb74901159bc5"
PATCH = "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"
LEFT, TOP, WIDTH, HEIGHT = 148, 134, 56, 250

def main():
    before = PATH.read_bytes()
    oldhash = hashlib.sha256(before).hexdigest()
    if oldhash == NEW_SHA:
        print("Avatar already matches supplied shadow-free image.")
        return
    if oldhash != OLD_SHA:
        raise RuntimeError(f"Unexpected portrait source SHA: {oldhash}")
    image = Image.open(io.BytesIO(before)).convert("RGBA")
    if image.size != (915, 2048):
        raise RuntimeError(f"Unexpected portrait dimensions: {image.size}")
    patch = zlib.decompress(base64.b64decode(PATCH))
    mask_size = (WIDTH * HEIGHT + 7) // 8
    flags = patch[:mask_size]
    pixels = patch[mask_size:]
    if len(flags) != 1750 or len(pixels) != 2412 * 4:
        raise RuntimeError("Invalid portrait delta")
    output = bytearray(image.tobytes())
    read_pos = 0
    for index in range(WIDTH * HEIGHT):
        if flags[index // 8] & (128 >> (index % 8)):
            x = LEFT + index % WIDTH
            y = TOP + index // WIDTH
            loc = (y * image.width + x) * 4
            output[loc:loc+4] = pixels[read_pos:read_pos+4]
            read_pos += 4
    if read_pos != len(pixels):
        raise RuntimeError("Portrait patch was not fully consumed")
    final = Image.frombytes("RGBA", image.size, bytes(output))
    with io.BytesIO() as stream:
        final.save(stream, "WEBP", lossless=True, method=6, exact=True)
        result = stream.getvalue()
    newhash = hashlib.sha256(result).hexdigest()
    if newhash != NEW_SHA:
        raise RuntimeError(f"Avatar checksum mismatch: {newhash}")
    PATH.write_bytes(result)
    print(f"Exact replacement complete: {len(result)} bytes ({newhash})")

if __name__ == "__main__":
    main()
