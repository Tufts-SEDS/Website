import re
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from tuftsseds.siteapps.events.models import Events
from tuftsseds.siteapps.events.views import MAX_EVENT_IMAGES

STATIC_EVENTS_DIR = Path(settings.BASE_DIR) / "static" / "images" / "events"
ARCHIVE_EVENTS_DIR = Path(settings.BASE_DIR).parent / "archive" / "images" / "events"


def template_references():
    """Event images hardcoded in templates, e.g. a photo on a team homepage."""
    refs = set()
    pattern = re.compile(r"images/events/([\w-]+)/([\w.-]+\.webp)")
    for template in (Path(settings.BASE_DIR) / "templates").rglob("*.html"):
        for folder, filename in pattern.findall(template.read_text(encoding="utf-8")):
            refs.add((folder, filename))
    return refs


class Command(BaseCommand):
    help = (
        f"Move every event photo past the first {MAX_EVENT_IMAGES} out of static/ "
        "and into archive/, keeping cover images and photos used in templates. "
        "Dry run unless --apply is passed."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true", help="Actually move the files."
        )

    def handle(self, *args, **options):
        apply = options["apply"]
        hardcoded = template_references()
        seen_folders = set()
        total_moved = 0

        for event in Events.objects.exclude(folder_name=None).order_by("folder_name"):
            folder = STATIC_EVENTS_DIR / event.folder_name
            seen_folders.add(event.folder_name)
            if not folder.is_dir():
                self.stdout.write(self.style.WARNING(f"Missing folder: {folder}"))
                continue

            keep = {
                f"{event.image_prepend_name}_{i}.webp"
                for i in range(1, MAX_EVENT_IMAGES + 1)
            }
            if event.cover_image:
                cover = event.cover_image.rstrip("/").rsplit("/", 1)[-1]
                keep.add(cover if cover.endswith(".webp") else cover + ".webp")
            keep |= {name for f, name in hardcoded if f == event.folder_name}

            to_move = sorted(p for p in folder.glob("*.webp") if p.name not in keep)
            self.stdout.write(
                f"{event.folder_name}: keeping {len(keep & {p.name for p in folder.glob('*.webp')})}, "
                f"archiving {len(to_move)}"
            )
            if not apply or not to_move:
                total_moved += len(to_move)
                continue

            dest = ARCHIVE_EVENTS_DIR / event.folder_name
            dest.mkdir(parents=True, exist_ok=True)
            for path in to_move:
                if (dest / path.name).exists():
                    self.stdout.write(self.style.WARNING(f"  already archived, skipping: {path.name}"))
                    continue
                shutil.move(str(path), str(dest / path.name))
                total_moved += 1

        for folder in sorted(p.name for p in STATIC_EVENTS_DIR.iterdir() if p.is_dir()):
            if folder not in seen_folders:
                self.stdout.write(self.style.WARNING(f"No event uses {folder}/, left untouched"))

        verb = "Moved" if apply else "Would move"
        self.stdout.write(self.style.SUCCESS(f"{verb} {total_moved} images to {ARCHIVE_EVENTS_DIR}"))
        if not apply:
            self.stdout.write("Dry run only. Re-run with --apply to move the files.")
