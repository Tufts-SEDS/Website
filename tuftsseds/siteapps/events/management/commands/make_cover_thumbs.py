"""Make a small thumbnail of each event's cover photo, and delete stray thumbnails.

Event lists, search results and the launches page show `<cover>_thumb.webp`
instead of the full photo (see Events.cover_thumb_url). Only covers get a
thumbnail; nothing else on the site uses one.

    python manage.py make_cover_thumbs            # dry run: shows what would change
    python manage.py make_cover_thumbs --apply    # write and delete files

Run it after adding an event or changing its cover, then commit the thumbnails.
It needs Pillow, which the deployed site doesn't install, so run it locally.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from tuftsseds.siteapps.events.images import THUMB_SUFFIX, cover_stem, thumb_name
from tuftsseds.siteapps.events.models import Events

STATIC_EVENTS_DIR = Path(settings.BASE_DIR) / "static" / "images" / "events"

THUMB_WIDTH = 800  # cards are ~400 px wide, so this is sharp on 2x screens
THUMB_QUALITY = 75


def plan_thumbs(events_dir, covers):
    """Work out which thumbnails to write and which to delete.

    `covers` is an iterable of (folder_name, cover_stem) pairs. Returns
    (to_write, to_delete, missing):
      to_write:  (photo, thumb) paths whose thumbnail is absent or older than the photo
      to_delete: thumbnails under events_dir that belong to no cover
      missing:   (folder_name, stem) pairs whose cover photo file doesn't exist
    Pure apart from reading the file system, so it can be tested without a database.
    """
    events_dir = Path(events_dir)
    expected, to_write, missing = set(), [], []
    for folder, stem in covers:
        photo = events_dir / folder / f"{stem}.webp"
        if not photo.is_file():
            missing.append((folder, stem))
            continue
        thumb = photo.with_name(thumb_name(stem))
        expected.add(thumb)
        if not thumb.is_file() or thumb.stat().st_mtime < photo.stat().st_mtime:
            to_write.append((photo, thumb))
    to_delete = sorted(
        p for p in events_dir.glob(f"*/*{THUMB_SUFFIX}.webp") if p not in expected
    )
    return to_write, to_delete, missing


def write_thumb(photo, thumb):
    from PIL import Image, ImageOps  # only needed here; not installed on Vercel

    with Image.open(photo) as img:
        img = ImageOps.exif_transpose(img)  # keep phone photos upright
        if img.width > THUMB_WIDTH:
            img.thumbnail((THUMB_WIDTH, THUMB_WIDTH * 10), Image.LANCZOS)
        icc = img.info.get("icc_profile")
        extra = {"icc_profile": icc} if icc else {}
        img.save(thumb, "WEBP", quality=THUMB_QUALITY, method=6, **extra)


class Command(BaseCommand):
    help = "Make a thumbnail of each event cover and delete stray thumbnails. Dry run unless --apply."

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="Write and delete files.")

    def handle(self, *args, **options):
        apply = options["apply"]
        covers = []
        for event in Events.objects.exclude(folder_name=None).exclude(folder_name="").order_by("folder_name"):
            stem = cover_stem(event.cover_image)
            if stem:
                covers.append((event.folder_name, stem))
            else:
                self.stdout.write(self.style.WARNING(f"No cover image: {event.slug}"))

        to_write, to_delete, missing = plan_thumbs(STATIC_EVENTS_DIR, covers)

        for folder, stem in missing:
            self.stdout.write(self.style.WARNING(f"Cover photo not found: {folder}/{stem}.webp"))
        for photo, thumb in to_write:
            self.stdout.write(f"  write  {thumb.relative_to(STATIC_EVENTS_DIR)}")
            if apply:
                write_thumb(photo, thumb)
        for thumb in to_delete:
            self.stdout.write(f"  delete {thumb.relative_to(STATIC_EVENTS_DIR)}")
            if apply:
                thumb.unlink()

        verb = "Wrote" if apply else "Would write"
        self.stdout.write(self.style.SUCCESS(
            f"{verb} {len(to_write)} thumbnail(s) and "
            f"{'deleted' if apply else 'would delete'} {len(to_delete)} stray one(s)."
        ))
        if not apply:
            self.stdout.write("Dry run only. Re-run with --apply to change files.")
