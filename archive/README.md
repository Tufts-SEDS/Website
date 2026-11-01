# Archived photos

I MOVED EVERYTHING TO THE SEDS GOOGLE DRIVE FOLDER /SEDS Documents/Archived Photos

Event photos that are no longer shown on the site. Event pages only show the
first 4 photos (`MAX_EVENT_IMAGES` in `tuftsseds/siteapps/events/views.py`), so
the rest were moved here by:

```bash
python manage.py archive_event_images          # dry run, shows what would move
python manage.py archive_event_images --apply  # moves the files
```

The folder layout matches `tuftsseds/static/images/events/`. To put a photo back
on the site, move it back into the matching static folder and make sure its
number is within the first 4 (or raise `MAX_EVENT_IMAGES`).

This folder is listed in `.vercelignore`, so nothing here is deployed.
