---
name: django-static-assets
description: Work with CSS, JS, images, and static files on the Tufts SEDS site, including minification and how Vercel serves them. Use when editing styles or scripts, adding images, or when a static file 404s in production.
---

# Static files

## Where things live
- `tuftsseds/static/css/`, `tuftsseds/static/js/`: site styles and scripts. Most files have a `.min.css`/`.min.js` twin, and the templates load the minified one.
- `tuftsseds/static/images/`: images. Event photos go under `images/events/<folder_name>/`, named `<image_prepend_name>_<n>.webp` for n = 1 to `total_images`, to match the `Events` fields.
- `tuftsseds/static/admin/`, `tuftsseds/static/debug_toolbar/`: collected from Django packages. Don't hand-edit these.
- Templates load assets with `{% load static %}` and `{% static 'css/style.min.css' %}`.

## Editing CSS or JS
1. Edit the non-minified source, e.g. `style.css`.
2. Regenerate the minified files with `python minify.py` from the repo root. It uses `jsmin` for JS and the Toptal API for CSS (needs internet), and it skips `apolo.core.js` and `apolo.init.js`.
3. Commit the source and `.min` files together. If you only change the source, production won't change, because the templates load the `.min` file.

`minify.py` builds its paths with Windows `\\` separators. On macOS/Linux, change them to `os.path.join` parts before running it.

## Deployment (Vercel)
- `vercel.json` serves `tuftsseds/static/**` directly as static files at `/static/...`, and sends every other request to the Django app in `api/index.py`.
- A file therefore only reaches production if it is committed under `tuftsseds/static/`.
- Browsers cache images, fonts and PDFs for 30 days and CSS/JS for 1 day (set per route in `vercel.json`).
- `{% static %}` adds `?v=<commit>` to every `.css` and `.js` URL on Vercel (`tuftsseds_core/storage.py`, using `VERCEL_GIT_COMMIT_SHA`), so each deploy makes browsers fetch fresh CSS/JS. Always link CSS/JS through `{% static %}`; a hard-coded `/static/...` path gets no version and can stay stale for a day.
- Images get no version, so to change an image right away, give it a new file name.
- Public pages are also cached at Vercel's CDN for 5 minutes (`tuftsseds_core/middleware.py`), so admin edits can take that long to show up.

## Adding photos
1. Convert them to `.webp` (`python webp_converter.py`) and put event photos in `images/events/<folder_name>/`.
2. Run `python optimize_images.py --apply` from the repo root. It shrinks photos to at most 1920 px (800 px for eboard headshots) and writes a `<name>_thumb.webp` next to every event photo. Event lists, search results and launch pages show the `_thumb` file (`Events.cover_thumb_url`), and fall back to the full photo if it's missing. Run it without `--apply` first to see what it will change; it skips files that are already done.
3. Commit the photos and their `_thumb` files together.

## Debugging a missing file
- Check that the path in `{% static %}` matches the file's real path and case. Vercel is case-sensitive, while Windows and macOS usually aren't.
- Check that the file is committed: `git ls-files tuftsseds/static | grep <name>`.
