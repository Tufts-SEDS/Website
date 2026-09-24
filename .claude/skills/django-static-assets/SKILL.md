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
- Keep images small: convert them to `.webp` and resize before committing. Large binaries make the repo slow for everyone.

## Debugging a missing file
- Check that the path in `{% static %}` matches the file's real path and case. Vercel is case-sensitive, while Windows and macOS usually aren't.
- Check that the file is committed: `git ls-files tuftsseds/static | grep <name>`.
