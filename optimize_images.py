"""
Shrink the site's static photos and make thumbnails for event cards.

Run this from the repo root after adding or replacing photos, and before
committing them:

    python optimize_images.py            # dry run: shows what would change
    python optimize_images.py --apply    # actually rewrite files

What it does:
  1. Resizes photos under tuftsseds/static/images and tuftsseds/static/WEBP_IMAGES
     so their longest side is at most MAX_SIDE (EBOARD_MAX_SIDE for headshots),
     and re-compresses ones that are stored far larger than they need to be.
     File names and formats stay the same, so templates don't change.
  2. Writes <name>_thumb.webp (THUMB_WIDTH wide) next to every event photo in
     static/images/events/<folder>/. Event lists, search results and launch
     pages show these instead of the full photo.

It is safe to run repeatedly: already-optimized images and up-to-date
thumbnails are skipped. Originals stay in git history and in Google Drive.
"""

import argparse
import io
import os
from pathlib import Path

from PIL import Image, ImageOps

STATIC = Path(__file__).resolve().parent / "tuftsseds" / "static"
ROOTS = [STATIC / "images", STATIC / "WEBP_IMAGES"]
EVENTS_DIR = STATIC / "images" / "events"

MAX_SIDE = 1920
EBOARD_MAX_SIDE = 800  # headshots are shown at ~300 px
THUMB_WIDTH = 800  # cards are ~400 px wide, so this is sharp on 2x screens
WEBP_QUALITY = 80
THUMB_QUALITY = 75
JPEG_QUALITY = 82
# Re-encode files that use more bytes per pixel than this even if they're small
# enough already. A typical photo at the qualities above lands well below it,
# so files this script already wrote are left alone on later runs.
MAX_BYTES_PER_PIXEL = 0.35
# Files smaller than this are only touched if they need resizing.
MIN_RECOMPRESS_BYTES = 200 * 1024
# Only replace a file if the new version is at least this much smaller.
MIN_SAVING = 0.05

EXTENSIONS = {".webp", ".jpg", ".jpeg", ".png"}


def is_thumb(path):
    return path.stem.endswith("_thumb")


def max_side_for(path):
    return EBOARD_MAX_SIDE if "eboard" in path.parts else MAX_SIDE


def encode(img, suffix, quality=None):
    """Return the image encoded in the format matching `suffix`, as bytes."""
    buf = io.BytesIO()
    icc = img.info.get("icc_profile")
    extra = {"icc_profile": icc} if icc else {}
    if suffix == ".webp":
        img.save(buf, "WEBP", quality=quality or WEBP_QUALITY, method=6, **extra)
    elif suffix in (".jpg", ".jpeg"):
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.save(buf, "JPEG", quality=quality or JPEG_QUALITY, optimize=True, progressive=True, **extra)
    else:  # .png: lossless, only resizing makes it smaller
        img.save(buf, "PNG", optimize=True, **extra)
    return buf.getvalue()


def load(path):
    img = Image.open(path)
    # Bake in phone camera rotation so the image stays upright without EXIF
    return ImageOps.exif_transpose(img)


def optimize(path, apply):
    """Resize/re-compress one image in place. Returns bytes saved (0 if skipped)."""
    size = path.stat().st_size
    with load(path) as img:
        img.load()
        width, height = img.size
        limit = max_side_for(path)
        too_big = max(width, height) > limit
        bloated = (
            path.suffix.lower() != ".png"
            and size > MIN_RECOMPRESS_BYTES
            and size / (width * height) > MAX_BYTES_PER_PIXEL
        )
        if not (too_big or bloated):
            return 0
        if too_big:
            img.thumbnail((limit, limit), Image.LANCZOS)
        data = encode(img, path.suffix.lower())
    if len(data) > size * (1 - MIN_SAVING):
        return 0
    print(f"  {size // 1024:6d} KB -> {len(data) // 1024:5d} KB  {path.relative_to(STATIC)}")
    if apply:
        path.write_bytes(data)
    return size - len(data)


def make_thumb(path, apply):
    """Write <name>_thumb.webp next to an event photo. Returns 1 if written."""
    thumb = path.with_name(path.stem + "_thumb.webp")
    if thumb.exists() and thumb.stat().st_mtime >= path.stat().st_mtime:
        return 0
    if apply:
        with load(path) as img:
            img.load()
            if img.width > THUMB_WIDTH:
                img.thumbnail((THUMB_WIDTH, THUMB_WIDTH * 10), Image.LANCZOS)
            thumb.write_bytes(encode(img, ".webp", quality=THUMB_QUALITY))
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="rewrite files (default is a dry run)")
    args = parser.parse_args()

    print("Resizing / re-compressing photos" + ("" if args.apply else " (dry run)") + ":")
    saved = 0
    for root in ROOTS:
        for dirpath, _, filenames in os.walk(root):
            for name in sorted(filenames):
                path = Path(dirpath) / name
                if path.suffix.lower() in EXTENSIONS and not is_thumb(path):
                    saved += optimize(path, args.apply)

    thumbs = 0
    for path in sorted(EVENTS_DIR.glob("*/*.webp")):
        if not is_thumb(path):
            thumbs += make_thumb(path, args.apply)

    verb = "Saved" if args.apply else "Would save"
    print(f"\n{verb} {saved / 1024 / 1024:.1f} MB; {thumbs} event thumbnail(s) "
          f"{'written' if args.apply else 'to write'}.")
    if not args.apply:
        print("Run again with --apply to make these changes.")


if __name__ == "__main__":
    main()
