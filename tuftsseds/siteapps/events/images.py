"""Where an event's photos live in static/.

Shared by the Events model (cover_url, cover_thumb_url) and the image
management commands, so they always agree on file names. Keep this module
free of Pillow: it is imported by the web app, which doesn't install it.
"""

from urllib.parse import urlsplit

THUMB_SUFFIX = "_thumb"


def cover_stem(value):
    """Return an event cover's file name without ".webp", or None if there is none.

    Events.cover_image normally holds a bare name such as "kidsday_4". It is a
    URLField, though, so a path or URL ending in that name, with or without
    ".webp", gives the same result.
    """
    if not value:
        return None
    name = urlsplit(value.strip()).path.rstrip("/").rsplit("/", 1)[-1]
    if name.lower().endswith(".webp"):
        name = name[: -len(".webp")]
    return name or None


def thumb_name(stem):
    """File name of the thumbnail for the photo `<stem>.webp`."""
    return f"{stem}{THUMB_SUFFIX}.webp"
